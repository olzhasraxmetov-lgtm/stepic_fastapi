from fastapi import APIRouter, Depends, Request, Query

from app.core.dependencies import get_current_user
from app.core.dependencies import get_purchase_service
from app.models.user import UserORM
from app.schemas.course import CourseResponse
from app.schemas.purchase import PurchaseDetailResponse
from app.services.purchase import PurchaseService

purchase_router = APIRouter(tags=["Purchase"])


@purchase_router.get('/purchases/success', summary='После успешной оплаты курса перенаправляет на этот эндпоинт')
async def payment_success_page(
        payment_id: int = Query(...),
        purchase_service: PurchaseService = Depends(get_purchase_service),
):
    return await purchase_service.handle_payment_status(payment_id)

@purchase_router.post('/webhook',
                      summary="Обработка уведомлений от ЮKassa",
                      description="Принимает POST-запросы от платежной системы при изменении статуса платежа"
                      )
async def yookassa_webhook(
    request: Request,
    purchase_service: PurchaseService = Depends(get_purchase_service),
):
    data = await  request.json()
    return await purchase_service.webhook_logic(data)

@purchase_router.get('/purchases/my', response_model=list[CourseResponse], summary='Получить список моих купленных курсов')
async def get_my_purchases(
        user: UserORM = Depends(get_current_user),
        purchase_service: PurchaseService = Depends(get_purchase_service),
):
    return await purchase_service.get_my_courses(user_id=user.id)

@purchase_router.post('/courses/{course_id}/purchase', summary='Купить курс')
async def create_purchase(
        course_id: int,
        user: UserORM = Depends(get_current_user),
        purchase_service: PurchaseService = Depends(get_purchase_service),
):
    confirmation_url = await purchase_service.initiate_purchase(course_id, user)
    return {"confirmation_url": confirmation_url}

@purchase_router.get('/purchases/{purchase_id}', response_model=PurchaseDetailResponse, summary='Получить детальную информацию о покупке')
async def get_purchase_detail(
        purchase_id: int,
        user: UserORM = Depends(get_current_user),
        purchase_service: PurchaseService = Depends(get_purchase_service),
):
    return await purchase_service.get_payment_detail_by_id(user_id=user.id, purchase_id=purchase_id)


