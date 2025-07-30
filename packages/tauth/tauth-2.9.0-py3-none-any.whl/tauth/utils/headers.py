import inspect
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import BackgroundTasks, Request, Security
from fastapi.security import APIKeyHeader
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase

UserEmail = Annotated[
    str | None,
    Security(
        APIKeyHeader(
            name="X-User-Email",
            scheme_name="X-User-Email",
            description="Ignore when using OAuth.",
            auto_error=False,
        ),
    ),
]

AccessTokenHeader = Annotated[
    HTTPAuthorizationCredentials | None,
    Security(HTTPBase(scheme="bearer", auto_error=False)),
]
ImpersonateEntityHandleHeader = Annotated[
    str | None,
    Security(
        APIKeyHeader(
            name="X-Impersonate-Entity-Handle",
            scheme_name="X-Impersonate-Entity-Handle",
            description="Impersonate another entity.",
            auto_error=False,
        ),
    ),
]
ImpersonateEntityOwnerHeader = Annotated[
    str | None,
    Security(
        APIKeyHeader(
            name="X-Impersonate-Entity-Owner",
            scheme_name="X-Impersonate-Entity-Owner",
            description="Impersonate another entity.",
            auto_error=False,
        ),
    ),
]

AuthHeaders = Annotated[
    *tuple[
        UserEmail,
        AccessTokenHeader,
        ImpersonateEntityHandleHeader,
        ImpersonateEntityOwnerHeader,
    ],
    "Headers required for authentication.",
]

AuthHeaderInjectorParams = Annotated[
    *tuple[Request, BackgroundTasks, AuthHeaders],
    "Parameter sequence for auth_headers_injector.",
]


def auth_headers_injector(
    auth_fn: Callable[
        [AuthHeaderInjectorParams], Any | Coroutine[Any, Any, Any]
    ],
) -> Callable[[AuthHeaderInjectorParams], Any]:
    async def async_wrapper(
        request: Request,
        background_tasks: BackgroundTasks,
        user_email: UserEmail = None,
        authorization: AccessTokenHeader = None,
        impersonate_entity_handle: ImpersonateEntityHandleHeader = None,
        impersonate_entity_owner: ImpersonateEntityOwnerHeader = None,
    ):
        result = await auth_fn(
            request,
            background_tasks,
            user_email,
            authorization,
            impersonate_entity_handle,
            impersonate_entity_owner,
        )
        return result

    def sync_wrapper(
        request: Request,
        background_tasks: BackgroundTasks,
        user_email: UserEmail = None,
        authorization: AccessTokenHeader = None,
        impersonate_entity_handle: ImpersonateEntityHandleHeader = None,
        impersonate_entity_owner: ImpersonateEntityOwnerHeader = None,
    ):
        result = auth_fn(
            request,
            background_tasks,
            user_email,
            authorization,
            impersonate_entity_handle,
            impersonate_entity_owner,
        )
        return result

    if inspect.iscoroutinefunction(auth_fn):
        return async_wrapper
    return sync_wrapper
