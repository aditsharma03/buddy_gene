import os
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, HTTPException, File, Form
from fastapi.responses import JSONResponse

from services.openAiService import generateTestCases, generateFromManualFiles
from services.jiraService import getJiraTicketDetails, createIssue


router = APIRouter()

@router.get("/checkhealth")
def checkhealth():
    return {
        "checkhealth": "The app is working fine.",
    }



# ----- Constants Setup -----
ALLOWED_EXT = {
    ".png", ".jpg", ".jpeg", ".pdf", ".fig",
    ".csv", ".xlsx", ".json", ".md", ".txt"
}

ALLOWED_MIME = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "text/markdown",
    "text/plain",
    "application/octet-stream"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILE_COUNT = 20



def validate_file(file: UploadFile):
    """
    Equivalent to the 'fileFilter' function.
    Raises an error if the file type is not allowed.
    """
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower() 
    mime = (file.content_type or "").lower()

    if ext in ALLOWED_EXT or mime in ALLOWED_MIME:
        return True

    if ext in [".csv", ".xlsx", ".fig"]:
        return True

    raise HTTPException(status_code=400, detail="Unsupported file type")




# ----- Routes -----

@router.post("/generate")
async def generate_route(
    files: List[UploadFile] = File(default=[]), 
    jiraText: str = Form(""), 
    mode: str = Form(""),
    ticketId: str = Form("")
):
    try:
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Too many files (limit 10)")

        processed_files = []
        
        for f in files:
            validate_file(f) 
            
            file_content = await f.read() 
            
            processed_files.append({
                "originalname": f.filename,
                "mimetype": f.content_type,
                "size": len(file_content),
                "buffer": file_content 
            })

        print(f"📝 Mode: {mode}")
        print(f"🎟️ Ticket: {ticketId}")
        print(f"📄 jiraText length: {len(jiraText)}")
        
        log_files = [
            {"name": f["originalname"], "type": f["mimetype"], "bytes": f["size"]} 
            for f in processed_files
        ]
        print(f"📎 files: {log_files}")

        result = await generateTestCases(jiraText, mode)

        return {"success": True, "result": result}

    except Exception as error:
        print(f"❌ Error in /generate route: {error}")
        
        # Converting the Exception object to string to check the message
        err_msg = str(error)
        message = "Error generating test cases."
        
        # Checking if it was our validation error
        if "Unsupported file type" in err_msg:
             message = "Only PNG, JPG, JPEG, PDF, FIG files are allowed."
        
        # Return 500 response
        return JSONResponse(
            status_code=500, 
            content={"success": False, "message": message}
        )





class JiraTicketReq(BaseModel):
    ticketId: str

@router.post("/jira-ticket")
async def get_jira_ticket(req: JiraTicketReq):
    try:
        text = await getJiraTicketDetails(req.ticketId)
        return {"success": True, "jiraText": text}

    except Exception as error:
        print(f"❌ /jira-ticket error: {error}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to fetch JIRA ticket."}
        )




class JiraCreateReq(BaseModel):
    projectKey: Optional[str] = None
    issueType: str = "Story"          # Default value
    summary: str                      # Required (No default)
    description: str = ""
    acceptanceCriteria: List[str] = []
    reporterEmail: Optional[str] = None
    reporterAccountId: Optional[str] = None

@router.post("/jira/create")
async def create_jira_ticket_route(req: JiraCreateReq):
    try:
        project_key = req.projectKey or os.getenv("JIRA_DEFAULT_PROJECT")
        if not project_key:
            return JSONResponse(
                status_code=400, 
                content={"success": False, "message": "projectKey required"}
            )

        # We construct the dictionary to pass to the function
        data = await createIssue({
            "projectKey": project_key,
            "issueType": req.issueType,
            "summary": req.summary,
            "description": req.description,
            "acceptanceCriteria": req.acceptanceCriteria,
            "reporterEmail": req.reporterEmail,
            "reporterAccountId": req.reporterAccountId,
        })

        return {"success": True, "issueKey": data["key"], "issueId": data["id"]}

    except Exception as e:
        print(f"❌ /jira/create: {e}")
        error_msg = "Failed to create Jira ticket."
        
        # If using 'requests' library, errors have a .response attribute
        if hasattr(e, "response") and e.response is not None:
            try:
                # e.response.data in JS is usually e.response.json() in Python
                rsp = e.response.json() 
                
                # Logic: rsp?.errorMessages?.[0] || rsp?.errors || rsp
                if "errorMessages" in rsp and rsp["errorMessages"]:
                    error_msg = rsp["errorMessages"][0]
                elif "errors" in rsp:
                    error_msg = str(rsp["errors"])
                else:
                    error_msg = str(rsp)
            except Exception:
                # If json parsing fails, fall back to string representation
                error_msg = str(e)
        else:
            error_msg = str(e)

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": error_msg}
        )



@router.post("/manual/generate")
async def manual_generate_route(
    manualFiles: List[UploadFile] = File(default=[]), 
    mode: str = Form("")
):
    try:
        if len(manualFiles) > 20:
            raise HTTPException(status_code=400, detail="Too many files (limit 20)")

        processed_files = []
        for f in manualFiles:
            validate_file(f)
            
            file_content = await f.read()
            processed_files.append({
                "originalname": f.filename,
                "mimetype": f.content_type,
                "size": len(file_content),
                "buffer": file_content
            })

        # Passing the list of file dicts and the mode string
        service_result = await generateFromManualFiles(processed_files, mode)
        
        text = service_result.get("text")
        cases_count = service_result.get("casesCount")

        return {
            "success": True, 
            "result": text, 
            "count": cases_count
        }

    except Exception as e:
        print(f"❌ /manual/generate error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e) or "Server error"}
        )
