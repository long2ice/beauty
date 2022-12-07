from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel

from beauty.depends import auth_required
from beauty.models import Feedback

router = APIRouter()


class FeedbackBody(BaseModel):
    content: str = Body(..., max_length=200)


@router.post("")
async def add_feedback(body: FeedbackBody, user_id=Depends(auth_required)):
    await Feedback.create(content=body.content, user_id=user_id)
