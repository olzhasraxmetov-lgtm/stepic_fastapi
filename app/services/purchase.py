from decimal import Decimal
from typing import Any
from uuid import uuid4

from anyio import to_thread
from loguru import logger
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.exceptions import ForbiddenException
from app.helpers.purchase_status import PurchaseStatus
from app.models.course import CourseORM
from app.models.user import UserORM
from app.repositories.course import CourseRepository
from app.repositories.purchase import PurchaseRepository
from app.schemas.purchase import PurchaseDetailResponse


class PurchaseService:
    def __init__(self, purchase_repo: PurchaseRepository, course_repo: CourseRepository,  shop_id: str, secret_key: str):
        self.purchase_repo = purchase_repo
        self.course_repo = course_repo
        self.shop_id = shop_id
        self.secret_key = secret_key
        Configuration.account_id = self.shop_id
        Configuration.secret_key = self.secret_key

    async def create_yookassa_payment(self,*,order_id: int, amount: Decimal, user_email: str, description: str,) -> dict[str, Any]:

        if not self.shop_id or not self.secret_key:
            raise RuntimeError("Задайте YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в .env")
        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f'https://learnedly-unportioned-courtney.ngrok-free.dev/purchases/success?payment_id={order_id}',
            },
            "capture": True,
            "description": description,
            "metadata": {
                "order_id": order_id,
            },
            "receipt": {
                "customer": {
                    "email": user_email,
                },
                "items": [
                    {
                        "description": description[:128],
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{amount:.2f}",
                            "currency": "RUB",
                        },
                        "vat_code": 1,
                        "payment_mode": "full_prepayment",
                        "payment_subject": "commodity",
                    },
                ],
            },
        }

        def _request() -> Any:
            return Payment.create(payload, str(uuid4()))

        payment = await to_thread.run_sync(_request)

        confirmation_url = getattr(payment.confirmation, "confirmation_url", None)

        return {
            "id": payment.id,
            "status": payment.status,
            "confirmation_url": confirmation_url,
        }

    async def initiate_purchase(self, course_id: int, user: UserORM):
        course: CourseORM | None = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundException(message='Курс не найден')

        existing_purchase = await self.purchase_repo.get_purchase_by_user_and_course(
            user_id=user.id,
            course_id=course.id,
        )
        if existing_purchase and existing_purchase.status == PurchaseStatus.SUCCEEDED:
            raise BadRequestException(message='Курс уже куплен')

        purchase = await self.purchase_repo.upsert_purchase({
            "user_id": user.id,
            "course_id": course.id,
            "price_paid": course.price,
            "payment_id": "pending_id",
            "status": PurchaseStatus.PENDING,
        })

        await self.purchase_repo.session.flush()

        payment_data = await self.create_yookassa_payment(
            order_id=purchase.id,
            amount=course.price,
            user_email=user.email,
            description=f"Оплата курса: {course.title}"
        )

        purchase.payment_id = payment_data["id"]
        await self.purchase_repo.session.commit()

        return payment_data["confirmation_url"]

    async def webhook_logic(self, event_data: dict):
        """Парсинг уведомления и маршрутизация логики."""
        try:
            notification_object = WebhookNotificationFactory().create(event_data)
            payment_object = notification_object.object

            await self.handle_webhook(
                payment_id=payment_object.id,
                status=payment_object.status
            )
            return {"status": "ok"}
        except Exception as e:
            logger.warning('Webhook error: %s', e)
            return {"status": "error", "message": str(e)}


    async def handle_webhook(self, payment_id: str, status: PurchaseStatus):
        purchase = await self.purchase_repo.get_payment_by_id(payment_id)

        if not purchase:
            raise NotFoundException(message=f'Payment {payment_id} not found')

        if status == PurchaseStatus.SUCCEEDED:
            purchase.status = PurchaseStatus.SUCCEEDED
        elif status == PurchaseStatus.CANCELED:
            purchase.status = PurchaseStatus.CANCELED

        await self.purchase_repo.session.commit()

    async def get_my_courses(self, user_id: int):
        return await self.purchase_repo.get_purchased_courses(user_id=user_id)

    async def handle_payment_status(self, payment_id: int):
        purchase = await self.purchase_repo.get_by_id_with_courses(payment_id)

        if not purchase:
            return {
                "status": "error",
                "message": "Покупка не найдена. Если вы уверены, что оплатили, обратитесь в поддержку."
            }
        if purchase.status == PurchaseStatus.SUCCEEDED:
            return {
                "status": "success",
                "message": f"Курс '{purchase.course.title}' успешно оплачен!",
                "course_id": purchase.course_id,
                "order_id": purchase.id
            }
        return {
            "status": "pending",
            "message": "Платеж обрабатывается. Обновите страницу через несколько секунд.",
            "course_id": purchase.course_id
        }


    async def get_payment_detail_by_id(self, purchase_id: int, user_id: int) -> PurchaseDetailResponse:
        purchase = await self.purchase_repo.get_by_id_with_courses(purchase_id)

        if not purchase:
            raise NotFoundException(message="Покупка не найдена")

        if purchase.user_id != user_id:
            raise ForbiddenException(message='У вас нет доступа к этой информаций')

        return PurchaseDetailResponse.model_validate(purchase)