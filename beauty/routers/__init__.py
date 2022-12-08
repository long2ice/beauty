from fastapi import APIRouter, Depends

from beauty.depends import sign_required
from beauty.routers import auth, collection, feedback, picture, user

router = APIRouter()

signed_router = APIRouter(dependencies=[Depends(sign_required)])

signed_router.include_router(picture.router, prefix="/picture", tags=["Picture"])
signed_router.include_router(collection.router, prefix="/collection", tags=["Collection"])
signed_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
signed_router.include_router(user.router, prefix="/user", tags=["User"])
signed_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])

router.include_router(signed_router)
