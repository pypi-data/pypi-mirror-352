import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app


@pytest.fixture
def test_client() -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


async def test_add(test_client: AsyncClient):
    response = await test_client.get("/calculator/add", params={"a": 1, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 3}


async def test_subtract(test_client: AsyncClient):
    response = await test_client.get(
        "/calculator/subtract", params={"a": 5, "b": 3}
    )
    assert response.status_code == 200
    assert response.json() == {"result": 2}


async def test_multiply(test_client: AsyncClient):
    response = await test_client.get(
        "/calculator/multiply", params={"a": 4, "b": 2}
    )
    assert response.status_code == 200
    assert response.json() == {"result": 8}


async def test_divide(test_client: AsyncClient):
    response = await test_client.get(
        "/calculator/divide", params={"a": 10, "b": 2}
    )
    assert response.status_code == 200
    assert response.json() == {"result": 5}


async def test_divide_by_zero(test_client: AsyncClient):
    response = await test_client.get(
        "/calculator/divide", params={"a": 10, "b": 0}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot divide by zero."
