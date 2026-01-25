import pytest
from decimal import Decimal
from app.models.user import UserORM
from sqlalchemy import update, select
from app.helpers.user_role import UserRoleEnum
from app.core.config import config


@pytest.mark.asyncio
async def test_register_user_success(client, db_session):
    data = {
        'username': 'regular_user',
        'email': 'regular@example.com',
        'password': 'faked_password',
        'full_name': 'Olzhas Regular',
    }

    response = await client.post('/user/register', json=data)
    assert response.status_code == 201

    db_query = await db_session.scalars(
        select(UserORM).filter(UserORM.email == data['email'])
    )
    res = db_query.first()
    assert res.username == data['username']
    assert res.email == data['email']
    assert res.full_name == data['full_name']
    assert res.hashed_password != data['password']

@pytest.mark.asyncio
async def test_register_existing_user(client, db_session):
    data = {
        'username': 'regular_user',
        'email': 'regular@example.com',
        'password': 'faked_password',
        'full_name': 'Olzhas Regular',
    }

    response = await client.post('/user/register', json=data)
    assert response.status_code == 201

    response_existing_user = await client.post('/user/register', json=data)
    assert response_existing_user.status_code == 409

@pytest.mark.asyncio
async def test_login_user_success(client, test_author):
    login_data = {
        "username": test_author.username,
        "password": "fake_hashed_password"
    }

    response = await client.post('/user/login', data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'

@pytest.mark.asyncio
async def test_get_my_profile_success(client, test_author):
    response = await client.get(f'/user/my_profile')
    assert response.status_code == 200

    data = response.json()
    assert data['email'] == test_author.email
    assert data['username'] == test_author.username

@pytest.mark.asyncio
async def test_get_my_profile_failure(unauth_client):
    response = await unauth_client.get('/user/my_profile')
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_my_profile_bad_token(unauth_client):
    headers = {"Authorization": "Bearer fake_token_here"}
    response = await unauth_client.get('/user/my_profile', headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_my_profile_success(client, test_author):
    response = await client.get(f'/user/my_profile')
    assert response.status_code == 200

    update_data = {
        'username': 'my_new_username',
        'full_name': 'my_new_full_name',
    }

    response = await client.put(f'/user/my_profile', json=update_data)
    assert response.status_code == 200

    assert response.json()['full_name'] == 'my_new_full_name'
    assert response.json()['username'] == 'my_new_username'


@pytest.mark.asyncio
async def test_update_my_profile_unauthorized(unauth_client):
    update_data = {'username': 'hacker_nick'}
    response = await unauth_client.put('/user/my_profile', json=update_data)

    assert response.status_code == 401
    assert response.json()['detail'] == "Not authenticated"

@pytest.mark.asyncio
async def test_update_my_profile_invalid_data(client):
    update_data = {
        'username': 'olzh',
        'email': 'olzhas@example.com',
    }

    response = await client.put(f'/user/my_profile', json=update_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_user_role_unauthorized(unauth_client, test_author):
    new_role = UserRoleEnum.ADMIN.value
    response = await unauth_client.patch(f'/user/admin/{test_author.id}/role', json={'role': new_role})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_user_role_forbidden(client, test_author):
    new_role = UserRoleEnum.ADMIN.value
    response = await client.patch(f'/user/admin/{test_author.id}/role', json={'role': new_role})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_role_success(admin_client, test_author, db_session):
    new_role = UserRoleEnum.ADMIN.value
    response = await admin_client.patch(f'/user/admin/{test_author.id}/role', json={'role': new_role})
    assert response.status_code == 200

    await db_session.refresh(test_author)
    assert test_author.role == UserRoleEnum.ADMIN

@pytest.mark.asyncio
async def test_update_user_role_not_found(admin_client, test_author):
    new_role = UserRoleEnum.ADMIN.value
    response = await admin_client.patch(f'/user/admin/123/role', json={'role': new_role})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_public_user_profile_success(unauth_client, test_author):
    response = await unauth_client.get(f'/user/{test_author.id}/profile')
    assert response.status_code == 200
    data = response.json()
    assert 'username' in data
    assert 'full_name' in data

    assert 'password' not in data
    assert 'email' not in data

@pytest.mark.asyncio
async def test_get_public_user_profile_not_found(unauth_client, test_author):
    non_existent_id = 99999
    response = await unauth_client.get(f'/user/{non_existent_id}/profile')
    assert response.status_code == 404

    assert response.json()['detail'] == f"User with ID {non_existent_id} not found"

@pytest.mark.asyncio
async def test_register_admin_success(client):
    data = {
        'username': 'test_admin',
        'email': 'admin@example.com',
        'full_name': 'test_admin',
        'password': 'fake_admin_password',
        'admin_secret_key': config.ADMIN_SECRET_KEY
    }
    response = await client.post('/user/register/admin', json=data)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_register_admin_failure_wrong_key(client):
    data = {
        'username': 'test_admin',
        'email': 'admin@example.com',
        'full_name': 'test_admin',
        'password': 'fake_admin_password',
        'admin_secret_key': 'wrong_key'
    }
    response = await client.post('/user/register/admin', json=data)
    assert response.status_code == 403
    assert response.json()['detail'] == "Invalid admin secret key"