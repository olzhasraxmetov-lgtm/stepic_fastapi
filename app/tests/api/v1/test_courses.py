import pytest
from decimal import Decimal
from app.models.course import CourseORM
from sqlalchemy import update

@pytest.mark.asyncio
async def test_get_courses(client, db_session, test_course_published, test_author):
    """Тест получения списка курсов. Тест проверяет что отдаются только опубликованные курсы"""
    unpublished_course = CourseORM(
        title='Этот курс будет не опубликован изначально',
        description="Описание длиной более двадцати символов",
        price=Decimal("5000.00"),
        author_id=test_author.id,
        is_published=False
    )
    db_session.add(unpublished_course)
    await db_session.commit()

    r_get = await client.get('/course/')
    assert r_get.status_code == 200
    data = r_get.json()

    assert 'items' in data
    assert 'page' in data
    assert 'per_page' in data
    assert 'total' in data
    assert len(data['items']) >= 1

    for course in data['items']:
        assert course['is_published'] is True

@pytest.mark.asyncio
async def test_get_courses_with_pagination(client, test_course_published):
    """Тест получения списка курсов с пагинацией."""
    r_get = await client.get('/course/?page=1&per_page=1')
    assert r_get.status_code == 200

    data = r_get.json()

    assert len(data['items']) <= 1
    assert data['page'] == 1
    assert data['per_page'] == 1

@pytest.mark.asyncio
async def test_get_courses_with_price_filters(client, db_session,test_author):
    """Тест получения списка курсов с фильтрацией цен по min_price и max_price."""
    course_ok = CourseORM(
        title="Этот курс должен быть в выдаче",
        description="Описание длиной более двадцати символов",
        price=Decimal("5000.00"),
        author_id=test_author.id,
        is_published=True
    )
    course_bad = CourseORM(
        title="Этот курс должен быть отфильтрован",
        description="Описание длиной более двадцати символов",
        price=Decimal("200.00"),
        author_id=test_author.id,
        is_published=True
    )
    db_session.add_all([course_ok, course_bad])
    await db_session.commit()

    r_get = await client.get('/course/?min_price=1000&max_price=10000')
    assert r_get.status_code == 200
    data = r_get.json()

    prices = [float(c['price']) for c in data['items']]
    assert 5000.00 in prices
    assert 200.00 not in prices


@pytest.mark.asyncio
async def test_get_courses_invalid_filters(client):
    """Тест валидации фильтров"""
    response = await client.get('/course/?min_price=200&max_price=100')
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_courses_with_invalid_query_params(client, test_course_published):
    """Тест валидации фильтров для пагинаций"""
    r_get = await client.get('/course/?per_page=101&page=0')
    assert r_get.status_code == 422

@pytest.mark.asyncio
async def test_create_and_get_course(client, test_author):
    """Тест успешного создания курса"""
    course_data = {
        'title': 'Телеграм-боты на Python и AIOgram.',
        'description': 'В курсе рассмотрена актуальная 3-я версия библиотеки.',
        'price': 500,
    }

    response = await client.post('/course/', json=course_data)
    if response.status_code == 422:
        print(response.json())
    assert response.status_code == 201

    data = response.json()
    assert data['title'] == course_data['title']
    assert data['description'] == course_data['description']
    assert float(data['price']) == course_data['price']
    assert data['author_id'] == test_author.id
    assert data['is_published'] is False

@pytest.mark.asyncio
async def test_create_and_get_course_invalid_data(client):
    """Тест неуспешного создания курса с неверными данными"""
    course_data = {
        'title': '',
        'description': '',
        'price': -200,
    }

    response = await client.post('/course/', json=course_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_my_courses(client, test_author):
    """Тест для получения своих курсов"""
    response = await client.get('/course/my/')
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    for course in data:
        assert course['author_id'] == test_author.id

@pytest.mark.asyncio
async def test_get_empty_courses(client):
    """Тест проверяет что если у пользователя нет курсов, он получит пустой список"""
    response = await client.get('/course/my/')
    assert response.status_code == 200

    assert response.json() == []

@pytest.mark.asyncio
async def test_update_course(client, test_course):
    """Тест для успешного обновления курса"""
    update_data = {"title": "New title for this course"}

    response = await client.patch(f'/course/{test_course.id}', json=update_data)

    data = response.json()

    assert data['title'] == update_data['title']

    assert data['description'] == test_course.description
    assert float(data['price']) == test_course.price


@pytest.mark.asyncio
async def test_update_course_invalid_user(user_client, test_course):
    """Тест проверяет, что только авторизированный пользователь может обновить курс"""
    update_data = {"title": "New title for this course"}

    response = await user_client.patch(f'/course/{test_course.id}', json=update_data)

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_course_not_found(client, test_course):
    """Тест обновления несуществующего курса"""
    update_data = {"title": "New title for this course"}

    response = await client.patch(f'/course/999', json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_course(client, test_course):
    """Тест успешного удаления курса"""
    response = await client.delete(f'/course/{test_course.id}')

    assert response.status_code == 200
    r_get = await client.get(f'/course/{test_course.id}')
    assert r_get.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_not_found(client):
    """Тест удаления несуществующего курса"""
    response = await client.delete(f'/course/999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Course not found'

@pytest.mark.asyncio
async def test_delete_course_invalid_user(user_client, test_course):
    """Тест проверяет что только авторизированный пользователь может удалить курс"""
    response = await user_client.delete(f'/course/{test_course.id}')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_publish_course(client, test_course):
    """Тест успешной публикаций курса"""
    response = await client.post(f'/course/{test_course.id}/publish')

    assert response.status_code == 200

    data = response.json()

    assert data['is_published'] is True

@pytest.mark.asyncio
async def test_publish_course_invalid_user(user_client, test_course):
    """Тест проверяет что только авторизированный пользователь можешь опубликовать курс"""
    response = await user_client.post(f'/course/{test_course.id}/publish')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_course_by_id(client, test_course):
    """Тест успешного получения курса по id"""
    response = await client.get(f'/course/{test_course.id}')

    assert response.status_code == 200
    result = response.json()

    assert result['id'] == test_course.id
    assert result['title'] == test_course.title
    assert result['description'] == test_course.description
    assert float(result['price']) == float(test_course.price)
    assert result['author_id'] == test_course.author_id

#@pytest.mark.asyncio
# async def test_create_course_rate_limit(limiter_client):
#     """Тест проверяет что при попытке сделать более 2 запрос за минуту, выдаст ошибку"""
#     course_data = {"title": "New Course Title", "description": "Description more than 20 chars", "price": 100}
#
#     r1 = await limiter_client.post('/course/', json=course_data)
#     assert r1.status_code == 201
#
#     r2 = await limiter_client.post('/course/', json=course_data)
#     assert r2.status_code == 201
#
#     r3 = await limiter_client.post('/course/', json=course_data)
#     assert r3.status_code == 429
#     assert r3.json()['detail'] == "Too Many Requests"

@pytest.mark.asyncio
async def test_check_cache_data(client, db_session, test_course, init_redis):
    """
    Тест проверяет, что данные действительно берутся из кэша,
    даже если они изменились в основной базе данных.
    """
    redis = init_redis

    response = await client.get(f'/course/{test_course.id}')
    assert response.status_code == 200
    original_title = response.json()['title']

    keys = await redis.keys("*")
    assert len(keys) > 0, "Кэш не был создан в Redis!"

    await db_session.execute(
        update(CourseORM)
        .where(CourseORM.id == test_course.id)
        .values(title='New Ghost Title')
    )
    await db_session.commit()

    second_res = await client.get(f'/course/{test_course.id}')

    assert second_res.json()['title'] == original_title
    assert second_res.json()['title'] != 'New Ghost Title'
