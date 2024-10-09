import httpx
import pytest
from fastapi import status


# -- CREATE TESTS -- #


@pytest.mark.asyncio
async def test_create_submission(async_client: httpx.AsyncClient, authenticated_user: str):
    url = "/api/submission"
    data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    response = await async_client.post(url, json=data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_submission_unprocessable(async_client: httpx.AsyncClient, authenticated_user: str):
    url = "/api/submission"
    data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
    }
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    response = await async_client.post(url, json=data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_submission_unauthorized(async_client: httpx.AsyncClient):
    url = "/api/submission"
    data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }
    response = await async_client.post(url, json=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# -- PATCH TESTS -- #


@pytest.mark.asyncio
async def test_update_model(async_client: httpx.AsyncClient, authenticated_user: str):
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1"
    update_data = {
        "title": "Updated Model",
        "description": "This is an updated model description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_update_model_unauthorized(async_client: httpx.AsyncClient, authenticated_user: str):
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1"
    update_data = {
        "title": "Updated Model",
        "description": "This is an updated model description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    update_response = await async_client.patch(update_url, json=update_data)
    assert update_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_model_conflict(async_client: httpx.AsyncClient, authenticated_user: str):
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission 2",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1"
    update_data = {
        "title": "Test Submission 2",
        "description": "This is an updated model description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_update_model_not_found(async_client: httpx.AsyncClient, authenticated_user: str):
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/2"
    update_data = {
        "title": "Updated Model",
        "description": "This is an updated model description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_submission_status(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/status"
    update_data = {
        "status": "published",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_change_submission_not_found(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/2/status"
    update_data = {
        "status": "published",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_submission_status_forbidden(async_client: httpx.AsyncClient, authenticated_user: str):
    headers = {"Authorization": f"Bearer {authenticated_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/status"
    update_data = {
        "status": "published",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_review_submission(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/status"
    update_data = {
        "status": "in_review",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED

    update_url = "/api/submission/1/review"
    update_data = {
        "review_message": "This is a review message",
        "status": "request_for_changes"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_review_submission_conflict(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/review"
    update_data = {
        "review_message": "This is a review message",
        "status": "request_for_changes"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_review_submission_not_found(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/2/review"
    update_data = {
        "review_message": "This is a review message",
        "status": "request_for_changes"
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND

# -- GET TESTS -- #


@pytest.mark.asyncio
async def test_get_all_published_submissions(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/status"
    update_data = {
        "status": "published",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED

    url = "/api/submission/published"

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_all_pending_submissions(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    update_url = "/api/submission/1/status"
    update_data = {
        "status": "in_review",
    }

    update_response = await async_client.patch(update_url, json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_202_ACCEPTED

    url = "/api/submission/pending"

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_all_user_submissions(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    url = "/api/submission/user/1"

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


# -- DELETE TESTS -- #

@pytest.mark.asyncio
async def test_delete_submission(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    url = "/api/submission/test-submission"

    response = await async_client.delete(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_submission_not_found(async_client: httpx.AsyncClient, admin_user: str):
    headers = {"Authorization": f"Bearer {admin_user}"}
    create_url = "/api/submission"
    create_data = {
        "title": "Test Submission",
        "description": "This is a test submission description",
        "authors": "Test Author",
        "repository_url": "test-repo.com",
        "resource_title": "Test Resource",
        "resource_url": "test-resource.com",
        "modality": "rgb_only"
    }

    create_response = await async_client.post(create_url, json=create_data, headers=headers)

    assert create_response.status_code == status.HTTP_201_CREATED

    url = "/api/submission/test-submission-2"

    response = await async_client.delete(url, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
