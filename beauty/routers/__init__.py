from fastapi import APIRouter, Depends

from beauty.depends import sign_required
from beauty.routers import auth, collection, picture, proxy, user

router = APIRouter()

signed_router = APIRouter(dependencies=[Depends(sign_required)])

signed_router.include_router(picture.router, prefix="/picture", tags=["Picture"])
signed_router.include_router(collection.router, prefix="/collection", tags=["Collection"])
signed_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
signed_router.include_router(user.router, prefix="/user", tags=["User"])

router.include_router(proxy.router, prefix="", tags=["Proxy"])
router.include_router(signed_router)
