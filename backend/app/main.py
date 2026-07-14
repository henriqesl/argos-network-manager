from fastapi import FastAPI


app = FastAPI(
    title="MikroTik Fleet Manager API",
    description=(
        "Backend API for monitoring and managing MikroTik router fleets."
    ),
    version="0.1.0",
)


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    """Return basic information about the API."""

    return {
        "message": "MikroTik Fleet Manager API is running."
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return the current health status of the API."""

    return {
        "status": "ok"
    }