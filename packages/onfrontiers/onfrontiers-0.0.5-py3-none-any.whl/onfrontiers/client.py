"""Client utilities for interacting with the OnFrontiers GraphQL API.

This module provides authentication and a client class for executing GraphQL queries and mutations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport, HTTPXTransport
from httpx import BasicAuth

if TYPE_CHECKING:
    from graphql import DocumentNode

API_URL = "https://api.onfrontiers.com/graphql"

AUTH_MUTATION = gql(
    """
    mutation CreateToken($client_id: String!) {
		createToken(client_id: $client_id) {
			token
		}
	}
""",
)


def auth_username_password(
    email: str,
    password: str,
    *,
    client_id: str = "python-sdk",
    external_auth_token: str | None = None,
    url: str | None = None,
) -> str:
    """Authenticate with the OnFrontiers API using email and password, and return an access token.

    Parameters
    ----------
    email : str
        The user's email address.
    password : str
        The user's password.
    client_id : str, optional
        The client identifier (default is "python-sdk").
    external_auth_token : str or None, optional
        An optional external authentication token.
    url : str or None, optional
        The API URL to use (default is the production API).

    Returns
    -------
    str
        The access token received from the API.

    """
    url = url or API_URL

    headers = {}
    if external_auth_token:
        headers["X-OnFrontiers-External-Auth"] = external_auth_token

    transport = HTTPXTransport(
        url=url,
        auth=BasicAuth(email, password),
        headers=headers,
    )
    client = Client(transport=transport)

    resp = client.execute(  # pyright: ignore[reportUnknownMemberType]
        AUTH_MUTATION,
        variable_values={"client_id": client_id},
        get_execution_result=False,
    )
    token = resp["createToken"]["token"]
    if not isinstance(token, str):
        msg = f"Unexpected response type: {type(token)}"
        raise TypeError(msg)

    return token


async def async_auth_username_password(
    email: str,
    password: str,
    *,
    client_id: str = "python-sdk",
    external_auth_token: str | None = None,
    url: str | None = None,
) -> str:
    """Asynchronously authenticate with the OnFrontiers API using email and password, and return an access token.

    Parameters
    ----------
    email : str
        The user's email address.
    password : str
        The user's password.
    client_id : str, optional
        The client identifier (default is "python-sdk").
    external_auth_token : str or None, optional
        An optional external authentication token.
    url : str or None, optional
        The API URL to use (default is the production API).

    Returns
    -------
    str
        The access token received from the API.

    """
    url = url or API_URL

    headers = {}
    if external_auth_token:
        headers["X-OnFrontiers-External-Auth"] = external_auth_token

    transport = HTTPXAsyncTransport(
        url=url,
        auth=BasicAuth(email, password),
        headers=headers,
    )

    async with Client(transport=transport) as session:
        resp = await session.execute(  # pyright: ignore[reportUnknownMemberType]
            AUTH_MUTATION,
            variable_values={"client_id": client_id},
            get_execution_result=False,
        )
        token = resp["createToken"]["token"]
        if not isinstance(token, str):
            msg = f"Unexpected response type: {type(token)}"
            raise TypeError(msg)

        return token


class _OnFrontiers(ABC):
    def __init__(
        self,
        access_token: str,
        *,
        url: str | None = None,
    ) -> None:
        """Initialize the OnFrontiers client with an access token and optional API URL.

        Parameters
        ----------
        access_token : str
            The access token for authenticating API requests.
        url : str or None, optional
            The API endpoint URL (default is the production API).

        """
        self.url = url or API_URL

        self._set_access_token(access_token)

    @abstractmethod
    def _set_access_token(self, access_token: str) -> None:
        pass


class OnFrontiers(_OnFrontiers):
    """Synchronous client for interacting with the OnFrontiers GraphQL API.

    This class provides methods to execute GraphQL queries and mutations using an access token.

    Attributes
    ----------
    client : Client
        The underlying GraphQL client instance.
    url : str
        The API endpoint URL.

    """

    def _set_access_token(self, access_token: str) -> None:
        headers = {"Authorization": f"Bearer {access_token}"}
        self.client = Client(
            transport=HTTPXTransport(url=self.url, headers=headers),
        )

    def execute(
        self,
        doc: DocumentNode,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation with the provided document and variables.

        Parameters
        ----------
        doc : DocumentNode
            The GraphQL query or mutation document to execute.
        **kwargs : dict[str, Any]
            Variables to pass to the GraphQL operation.

        Returns
        -------
        dict[str, Any]
            The result of the GraphQL execution.

        """
        return self.client.execute(
            doc,
            variable_values=kwargs,
            get_execution_result=False,
        )


class AsyncOnFrontiers(_OnFrontiers):
    """Asynchronous client for interacting with the OnFrontiers GraphQL API.

    This class provides asynchronous methods to execute GraphQL queries and mutations using an access token.

    Attributes
    ----------
    client : Client
        The underlying asynchronous GraphQL client instance.
    url : str
        The API endpoint URL.

    """

    def _set_access_token(self, access_token: str) -> None:
        headers = {"Authorization": f"Bearer {access_token}"}
        self.client = Client(
            transport=HTTPXAsyncTransport(url=self.url, headers=headers),
        )

    async def execute(
        self,
        doc: DocumentNode,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Asynchronously execute a GraphQL query or mutation with the provided document and variables.

        Parameters
        ----------
        doc : DocumentNode
            The GraphQL query or mutation document to execute.
        **kwargs : dict[str, Any]
            Variables to pass to the GraphQL operation.

        Returns
        -------
        dict[str, Any]
            The result of the GraphQL execution.

        """
        async with self.client as session:
            return await session.execute(  # type: ignore[no-any-return]
                doc,
                variable_values=kwargs,
                get_execution_result=False,
            )
