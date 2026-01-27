from fastapi import APIRouter
purchase_router = APIRouter(tags=["Purchase"])

@purchase_router.post('/courses/{course_id}/purchase')
async def create_purchase():
    pass

@purchase_router.get('/purchases/my')
async def get_my_purchases():
    pass

@purchase_router.get('/purchases/{purchase_id}')
async def get_purchase_detail():
    pass