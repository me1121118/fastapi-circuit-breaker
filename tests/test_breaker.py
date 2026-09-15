import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from fastapi_circuit_breaker import circuit_breaker

@pytest.fixture
def app():
    fastapi_app = FastAPI()
    should_fail = True

    async def fallback_func():
        return {"data": "cached_fallback"}

    @fastapi_app.get("/unstable")
    @circuit_breaker(failure_threshold=2, recovery_timeout=10.0, fallback=fallback_func)
    async def unstable_route():
        if should_fail:
            raise RuntimeError("Downstream API timeout")
        return {"data": "live_data"}

    fastapi_app.state.set_fail = lambda val: globals().update(should_fail=val)
    return fastapi_app

@pytest.mark.asyncio
async def test_circuit_breaker_trips_to_fallback(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Failure 1
        with pytest.raises(RuntimeError):
            await client.get("/unstable")

        # Failure 2 (reaches threshold -> trips OPEN)
        r2 = await client.get("/unstable")
        # Since fallback is provided, it gracefully returns fallback!
        assert r2.status_code == 200
        assert r2.json()["data"] == "cached_fallback"

        # Request 3: Fast-fail to fallback without even invoking the crashing function
        r3 = await client.get("/unstable")
        assert r3.status_code == 200
        assert r3.json()["data"] == "cached_fallback"
