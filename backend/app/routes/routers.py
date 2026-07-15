from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credential_cipher import (
    CredentialCipher,
    get_credential_cipher,
)
from app.db.database import get_database_session
from app.repositories.router import RouterRepository
from app.schemas.router import (
    RouterCreate,
    RouterListResponse,
    RouterResponse,
)


router = APIRouter(
    prefix="/routers",
    tags=["Routers"],
)


@router.get(
    "",
    response_model=RouterListResponse,
)
async def list_routers(
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
) -> RouterListResponse:
    """Return a paginated list of registered routers."""

    repository = RouterRepository(session)

    routers = await repository.list_routers(
        offset=offset,
        limit=limit,
    )

    total = await repository.count_routers()

    return RouterListResponse(
        items=routers,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post(
    "",
    response_model=RouterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_router(
    payload: RouterCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
    credential_cipher: Annotated[
        CredentialCipher,
        Depends(get_credential_cipher),
    ],
) -> RouterResponse:
    """Register a new router with encrypted credentials."""

    repository = RouterRepository(session)

    existing_router = await repository.get_by_management_ip(
        payload.management_ip
    )

    if existing_router is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A router with this management IP "
                "is already registered."
            ),
        )

    password_ciphertext = credential_cipher.encrypt(
        payload.password.get_secret_value()
    )

    try:
        router_record = await repository.create_router(
            name=payload.name,
            management_ip=payload.management_ip,
            public_ip=payload.public_ip,
            api_port=payload.api_port,
            username=payload.username,
            password_ciphertext=password_ciphertext,
        )

        await session.commit()
        await session.refresh(router_record)

    except IntegrityError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A router with this management IP "
                "is already registered."
            ),
        ) from exc

    return RouterResponse.model_validate(router_record)