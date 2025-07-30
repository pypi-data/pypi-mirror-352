from enum import Enum
from typing import Optional

from flink_gateway_api import Client

from resinkit_api.clients.sql_gateway.flink_operation import FlinkOperation
from resinkit_api.clients.sql_gateway.flink_session import FlinkSession
from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from flink_gateway_api.api.default import (
    cancel_operation,
    close_operation,
    get_operation_status,
)
from flink_gateway_api.types import UNSET

logger = get_logger(__name__)


class FlinkSqlGatewayNotFoundException(Exception):
    pass


class FlinkSqlGatewayOperationNotFoundError(FlinkSqlGatewayNotFoundException):
    pass


class FlinkSqlGatewaySessionNotFoundError(FlinkSqlGatewayNotFoundException):
    pass


def maybe_not_found_exception(exception: Exception) -> FlinkSqlGatewayNotFoundException | None:
    """Get the Flink operation exception type from an exception."""
    if hasattr(exception, "content"):
        content = exception.content.decode("utf-8")
        if "Can not find the submitted operation" in content:
            return FlinkSqlGatewayOperationNotFoundError(exception)
        elif "org.apache.flink.table.gateway.service.session.SessionManagerImpl.getSession" in content and "does not exist" in content:
            return FlinkSqlGatewaySessionNotFoundError(exception)
    return None


class FlinkSqlGatewayClient:
    """Client for managing calls to Flink SQL Gateway REST endpoint."""

    def __init__(self, gateway_url: Optional[str] = None):
        """Initialize the Flink SQL Gateway client.

        Args:
            gateway_url: The URL of the Flink SQL Gateway. If not provided,
                         it will use the URL from the settings.
        """
        self.gateway_url = gateway_url or settings.FLINK_SQL_GATEWAY_URL
        logger.info(f"Initializing Flink SQL Gateway client with URL: {self.gateway_url}")
        # TODO: read client params from settings
        self.client = Client(
            base_url=self.gateway_url,
            raise_on_unexpected_status=True,
            timeout=10,
        )

    def get_client(self) -> Client:
        return self.client

    def get_session(self, properties: Optional[dict] = None, session_name: Optional[str] = None, create_if_not_exist: bool = True) -> FlinkSession:
        """Get a Flink session instance.

        Args:
            properties: Session properties.
            session_name: Name of the session.

        Returns:
            FlinkSession: A session instance for the Flink SQL Gateway.
        """
        try:
            client = self.get_client()
            session = FlinkSession(client, properties, session_name, create_if_not_exist)
            if create_if_not_exist:
                session.open_sync()
            return session
        except Exception as e:
            not_found_exception = maybe_not_found_exception(e)
            if not_found_exception:
                raise not_found_exception
            raise e

    async def cancel_all_operations(self, session_handle: str, operation_handles: list[str]) -> None:
        """Cancel all operations in a session."""
        for operation_handle in operation_handles:
            try:
                await cancel_operation.asyncio(session_handle, operation_handle, client=self.client)
            except Exception as e:
                not_found_exception = maybe_not_found_exception(e)
                if not_found_exception:
                    raise not_found_exception
                raise e

    async def get_operation_status(self, session_handle: str, operation_handle: str) -> str:
        """Get the status of an operation."""
        try:
            response = await get_operation_status.asyncio(session_handle, operation_handle, client=self.client)
            if response.status == UNSET:
                return None
            return response.status
        except Exception as e:
            not_found_exception = maybe_not_found_exception(e)
            if not_found_exception:
                raise not_found_exception
            raise e
