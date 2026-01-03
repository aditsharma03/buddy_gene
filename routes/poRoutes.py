from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.openAiService import generate_with_openrouter

router = APIRouter(prefix="/po", tags=["PO Tools"])


# -------- Request Models --------
class OneLinerRequest(BaseModel):
    oneLiner: str


# -------- Button 1 — AC & User Story --------
@router.post("/generate-ac")
async def generate_ac(payload: OneLinerRequest):
    one_liner = payload.oneLiner.strip()

    if not one_liner:
        raise HTTPException(status_code=400, detail="oneLiner required")

    prompt = f"""
You are a Product Owner assistant. I will provide you with a single-line idea (one-liner summary) for a product feature. Your task is to transform it into a fully defined User Story with complete Acceptance Criteria.

Output Requirements:

User Story
Must follow the exact format:
User Story: As a <role>, I want <capability> so that <benefit>.

Acceptance Criteria:
- Bullet points only
- Clear, testable, complete sentences
- Include validation and edge cases
- No numbering, no markdown, no explanations

One-liner: {one_liner}
    """

    try:
        result = await generate_with_openrouter(
            prompt=prompt,
            max_tokens=800,
            temperature=0.2
        )
        return {"result": result}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate AC")


# -------- Button 2 — Grooming Plan --------
@router.post("/grooming")
async def grooming_plan():
    template = """
Grooming Agenda:
- Goal of session
- Tickets to discuss
- Estimation approach
- Owners & SMEs
- Outcomes & next steps

(Email sending & board creation to be integrated)
    """.strip()

    return {"result": template}


# -------- Button 3 — Sprint Planning --------
@router.post("/planning")
async def sprint_planning():
    template = """
Sprint Planning:
- Sprint Goal(s)
- Prioritized backlog (IDs)
- Capacity overview
- Risks/Dependencies
- Definition of Ready/Done

(Email sending & board creation to be integrated)
    """.strip()

    return {"result": template}


# -------- Button 4 — Retro Board --------
@router.post("/retro")
async def retro_board():
    template = """
Retro Board:
- Went well:
- Didn't go well:
- Ideas/Experiments:
- Action items (Owner, ETA):

(Export/share link & vote feature can be added later)
    """.strip()

    return {"result": template}


# -------- Button 5 — Capacity Board --------
@router.post("/capacity")
async def capacity_board():
    template = """
Capacity Board (example):
| Member | Velocity | Leaves/Meetings (hrs) | Effective Capacity (hrs) |
|--------|----------|------------------------|---------------------------|
| A      | 20 pts   | 6                      | 34                        |
| B      | 15 pts   | 4                      | 36                        |

(Next: pull calendar leaves & auto-calc)
    """.strip()

    return {"result": template}
