from fastapi import APIRouter

router = APIRouter()



@router.get("/checkhealth")
def checkhealth():
    return {
        "checkhealth": "The app is working fine.",
    }



