from fastapi import APIRouter, Depends, Query, Request
from starlette import status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.core.dependencies import get_course_service
from app.core.dependencies import get_current_user
from app.models.user import UserORM
from app.schemas.course import CourseResponse, CourseCreate, CourseUpdate, CourseList
from app.services.course import CourseService
from fastapi_cache.decorator import cache
course_router = APIRouter(
    prefix="/course",
    tags=["course"]
)

async def service_http_user_id(request: Request):
    return request.client.host


@course_router.get('/', response_model=CourseList,
                   dependencies=[Depends(RateLimiter(times=5, seconds=10, identifier=service_http_user_id))])
@cache(expire=30)
async def get_courses(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        min_price: float | None = Query(None, ge=0, description='Минимальная цена товара'),
        max_price: float | None = Query(None, ge=0, description='Максимальная цена товара'),
        course_service: CourseService = Depends(get_course_service),
) -> CourseList:
    print("\n[DEBUG] === ЗАПРОС ПРИШЕЛ В ФУНКЦИЮ (ИДЕМ В БАЗУ) ===\n")
    return await course_service.get_paginated_courses(
        page=page,
        per_page=per_page,
        min_price=min_price,
        max_price=max_price,
    )


@course_router.post('/', status_code=status.HTTP_201_CREATED, response_model=CourseResponse)
async def create_course(
        payload: CourseCreate,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.create_course(user, payload)

@course_router.get('/{course_id}', response_model=CourseResponse)
async def get_course(
        course_id: int,
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.get_by_id(course_id)

@course_router.get('/my/', response_model=list[CourseResponse])
async def get_my_courses(
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
) -> list[CourseResponse]:
    return await course_service.get_my_courses(user.id)

@course_router.patch('/{course_id}', response_model=CourseResponse)
async def update_course(
        payload: CourseUpdate,
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.update_course(
        current_user=user,
        course_id=course_id,
        payload=payload,
    )

@course_router.delete('/{course_id}')
async def delete_course(
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.delete_course(user,course_id)

@course_router.post('/{course_id}/publish')
async def publish_course(
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.publish_course(user,course_id)