from fastapi import APIRouter, Depends

from beauty.depends import sign_required

router = APIRouter(dependencies=[Depends(sign_required)])
