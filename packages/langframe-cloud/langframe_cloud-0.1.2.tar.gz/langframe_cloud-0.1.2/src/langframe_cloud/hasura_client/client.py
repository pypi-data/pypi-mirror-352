from langframe_cloud.hasura_client.generated_graphql_client import Client

X_HASURA_ROLE = "x-hasura-role"

X_HASURA_ORGANIZATION_ID = "x-hasura-organization-id"

X_HASURA_USER_ID = "x-hasura-user-id"

X_HASURA_USE_BACKEND_ONLY_PERMISSIONS = "x-hasura-use-backend-only-permissions"

X_HASURA_ADMIN_SECRET = (
    "x-hasura-admin-secret"  # nosec B105: not a secret, just a header name
)


class HasuraClient:
    """
    Wrapper around the generated GraphQL client providing additional functionality.
    """

    def __init__(self, graphql_uri: str, graphql_ws_uri: str, admin_secret: str = None):
        """
        Initialize the HasuraClient.

        Args:
            graphql_uri: The URL of the Hasura GraphQL endpoint
            admin_secret: Optional admin secret for admin access
        """
        self.admin_secret = admin_secret
        self.graphql_uri = graphql_uri
        self.graphql_ws_uri = graphql_ws_uri
        headers = {X_HASURA_ADMIN_SECRET: admin_secret} if admin_secret else {}
        self.admin_client = Client(
            url=graphql_uri, ws_url=graphql_ws_uri, headers=headers, ws_headers=headers
        )

    def get_admin_client(self):
        """
        Returns a GraphQL client configured with admin privileges.

        This client uses the admin secret for authentication and should be used sparingly,
        typically only for administrative operations that require full system access.
        Avoid using this client for regular user operations as it bypasses all permission checks.

        Returns:
            Client: A GraphQL client instance with admin privileges
        """
        return self.admin_client

    def get_user_client(self, auth_token: str):
        """
        Returns a GraphQL client configured for user-level access.

        This client is authenticated using the user's JWT token and should be used
        for read-only operations on behalf of a user. It respects Hasura's permission
        rules and is suitable for client-side queries.

        Args:
            auth_token (str): The JWT token of the authenticated user

        Returns:
            Client: A GraphQL client instance with user-level permissions
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        return Client(
            url=self.graphql_uri,
            ws_url=self.graphql_ws_uri,
            headers=headers,
            ws_headers=headers,
        )

    def get_backend_only_client(
        self, user_id: str, organization_id: str, hasura_role: str
    ):
        """
        Returns a GraphQL client configured for backend operations on behalf of a user.

        This client is used when making requests that are backend-protected, typically
        for operations that modify or create resources. It combines admin access with
        user context, allowing the backend to perform privileged operations while
        maintaining proper user attribution and permission checks.

        Args:
            user_id (str): The Database ID of the user on whose behalf the request is made
            organization_id (str): The Database ID of the organization the user belongs to (from the JWT token)
            hasura_role (str): The Hasura role to use for permission checks (from the JWT token)

        Returns:
            Client: A GraphQL client instance configured for backend operations
        """
        headers = {
            X_HASURA_ADMIN_SECRET: self.admin_secret,
            X_HASURA_USER_ID: user_id,
            X_HASURA_ORGANIZATION_ID: organization_id,
            X_HASURA_ROLE: hasura_role,
            X_HASURA_USE_BACKEND_ONLY_PERMISSIONS: "true",
        }
        return Client(
            url=self.graphql_uri,
            ws_url=self.graphql_ws_uri,
            headers=headers,
            ws_headers=headers,
        )
