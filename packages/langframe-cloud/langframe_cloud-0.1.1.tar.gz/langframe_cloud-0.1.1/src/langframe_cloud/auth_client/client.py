import logging

import requests

logger = logging.getLogger(__name__)

HASURA_ROLE = "X-Hasura-Role"
HASURA_ORGANIZATION_ID = "X-Hasura-Organization-Id"
HASURA_USER_ID = "X-Hasura-User-Id"

AUTH_RESPONSE_REQUIRED_FIELDS = [HASURA_ROLE, HASURA_ORGANIZATION_ID, HASURA_USER_ID]

TYPEDEF_INSTANCE_TO_API_URL = {
    "dev1": "https://api.dev1.typedef.engineering/",
}

API_AUTHORIZE_PATH = "v1/auth/token/authorize"

# Default timeout in seconds for all requests
TIMEOUT = 10


def authenticate_user(typedef_instance: str, token: str) -> tuple[str, str, str]:
    """
    Authenticates a user token by calling the auth provider, returns user metadata (user id, org id, role).
    """
    api_auth_endpoint = (
        f"{TYPEDEF_INSTANCE_TO_API_URL[typedef_instance]}/{API_AUTHORIZE_PATH}"
    )
    headers = {"authorization": f"Bearer {token}"}
    logger.debug(
        f"Authenticating user token: {token} with endpoint: {api_auth_endpoint}"
    )

    response = requests.get(api_auth_endpoint, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    for field in AUTH_RESPONSE_REQUIRED_FIELDS:
        if field not in data:
            raise Exception(f"No {field} in response: {data}")

    return (
        data[HASURA_USER_ID],
        data[HASURA_ORGANIZATION_ID],
        data[HASURA_ROLE],
    )


def get_user_token(
    auth_url: str, typedef_instance: str, client_id: str, client_secret: str
) -> str:
    """
    Gets a user token by calling the auth provider with the given client id and secret.

    Args:
        auth_url: The URL of the auth provider
        typedef_instance: The instance of the typedef instance (i.e. dev1)
        client_id: The client id
        client_secret: The client secret

    for dev testing use dev-0ozik42buwiy0al7.us.auth0.com
    """
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": f"{TYPEDEF_INSTANCE_TO_API_URL[typedef_instance]}",
        "grant_type": "client_credentials",
    }
    headers = {"content-type": "application/json"}

    logger.debug(
        f"Getting user token with payload: {payload} from auth_url: {auth_url}"
    )
    response = requests.post(
        f"{auth_url}/oauth/token", json=payload, headers=headers, timeout=TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise Exception(
            f"Error getting user token: {data['error']} details: {data['error_description']}"
        )
    if "access_token" not in data:
        raise RuntimeError("No access token returned from auth provider")

    return data["access_token"]
