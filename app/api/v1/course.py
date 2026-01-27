from fastapi import APIRouter, Depends, Query
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from starlette import status
from app.api.v1.purchase import purchase_router
from app.core.dependencies import get_course_service
from app.core.dependencies import get_current_user
from app.core.dependencies import service_http_user_id
from app.helpers.courses.cache_utils import invalidate_cache
from app.helpers.courses.cache_utils import item_key_builder
from app.models.user import UserORM
from app.schemas.course import CourseResponse, CourseCreate, CourseUpdate, CourseList
from app.services.course import CourseService
from app.api.v1.lesson import lesson_router
course_router = APIRouter(
    prefix="/courses",
)



@course_router.get('/', response_model=CourseList, tags=["Courses"])
@cache(expire=60, namespace="courses", coder=PickleCoder)
async def get_courses(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        min_price: float | None = Query(None, ge=0, description='Минимальная цена товара'),
        max_price: float | None = Query(None, ge=0, description='Максимальная цена товара'),
        course_service: CourseService = Depends(get_course_service),
) -> CourseList:
    return await course_service.get_paginated_courses(
         page=page,
         per_page=per_page,
         min_price=min_price,
         max_price=max_price,
     )

@course_router.post('/', status_code=status.HTTP_201_CREATED, response_model=CourseResponse, dependencies=[Depends(RateLimiter(times=2, minutes=1, identifier=service_http_user_id))], tags=["Courses"])
async def create_course(
        payload: CourseCreate,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    result = await course_service.create_course(user, payload)
    await invalidate_cache()
    return result

@course_router.get('/my/', response_model=list[CourseResponse], dependencies=[Depends(RateLimiter(times=5, seconds=10, identifier=service_http_user_id))], tags=["Courses"])
async def get_my_courses(
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
) -> list[CourseResponse]:
    return await course_service.get_my_courses(user.id)

@course_router.patch('/{course_id}', response_model=CourseResponse,
                     dependencies=[Depends(RateLimiter(times=5, minutes=1, identifier=service_http_user_id))], tags=["Courses"])
async def update_course(
        payload: CourseUpdate,
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    result = await course_service.update_course(
        current_user=user,
        course_id=course_id,
        payload=payload,
    )

    await invalidate_cache(course_id=course_id)

    return result

@course_router.delete('/{course_id}', dependencies=[Depends(RateLimiter(times=2, minutes=1, identifier=service_http_user_id))], tags=["Courses"])
async def delete_course(
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    result = await course_service.delete_course(user,course_id)
    await invalidate_cache(course_id=course_id)
    return result

@course_router.post('/{course_id}/publish', dependencies=[Depends(RateLimiter(times=2, minutes=1, identifier=service_http_user_id))], tags=["Courses"])
async def publish_course(
        course_id: int,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    result = await course_service.publish_course(user,course_id)
    await invalidate_cache(course_id=course_id)
    return  result



@course_router.get('/{course_id}', response_model=CourseResponse,tags=["Courses"])
@cache(expire=60, namespace='courses', key_builder=item_key_builder, coder=PickleCoder)
async def get_course(
        course_id: int,
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.get_by_id(course_id)

course_router.include_router(lesson_router, tags=["Lessons"])