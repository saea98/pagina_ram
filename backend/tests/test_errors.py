from httpx import AsyncClient


async def test_validation_error_is_spanish(client: AsyncClient) -> None:
    response = await client.post("/api/_validation-probe", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Revisa los datos enviados."
    assert body["error"]["fields"]["name"] == "Este campo es obligatorio."


async def test_not_found_format(client: AsyncClient) -> None:
    response = await client.get("/api/no-existe")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["message"] == "No encontramos lo que buscas."


async def test_domain_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/_missing")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "No encontramos ese recurso."


async def test_internal_error_hides_details(client: AsyncClient) -> None:
    response = await client.get("/api/_boom")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["message"] == "Ocurrió un error interno."
    assert "secret" not in response.text
