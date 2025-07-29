import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from langframe_cloud.hasura_client.generated_graphql_client import (
    Client,
    ExecutionDetails,
)
from langframe_cloud.hasura_client.generated_graphql_client import (
    TypedefExecutionStatusReferenceEnum as QUERY_STATE,
)
from langframe_cloud.hasura_client.generated_graphql_client.exceptions import (
    GraphQLClientError,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def get_query_execution_by_id(
    client: Client, query_execution_id: UUID
) -> Optional[ExecutionDetails]:
    try:
        query_response = await client.get_query_execution_details_by_id(
            query_execution_id
        )
        if not query_response.typedef_query_execution:
            return None
        return query_response.typedef_query_execution.pop()
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return None


async def get_queries_by_user_id(
    client: Client,
    user_id: UUID,
    limit: int = 10,
    offset: int = 0,
    status: Optional[QUERY_STATE] = None,
) -> List[ExecutionDetails]:
    try:
        if status is None:
            query_response = await client.list_query_execution_details_by_user_id(
                created_by_user_id=user_id, limit=limit, offset=offset
            )
        else:
            query_response = (
                await client.list_query_execution_details_by_user_id_and_status(
                    created_by_user_id=user_id,
                    status=status,
                    limit=limit,
                    offset=offset,
                )
            )
        return query_response.typedef_query_execution
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return []


async def get_queries_by_session_id(
    client: Client,
    session_id: UUID,
    limit: int = 10,
    offset: int = 0,
    status: Optional[QUERY_STATE] = None,
) -> List[ExecutionDetails]:
    try:
        if status is None:
            query_response = await client.list_query_execution_details_by_session_id(
                parent_execution_session_id=session_id,
                limit=limit,
                offset=offset,
            )
        else:
            query_response = (
                await client.list_query_execution_details_by_session_id_and_status(
                    parent_execution_session_id=session_id,
                    status=status,
                    limit=limit,
                    offset=offset,
                )
            )
        return query_response.typedef_query_execution
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return []


async def query_execution_subscription(
    client: Client,
    query_execution_id: UUID,
    wait_for_states: Optional[List[QUERY_STATE]] = None,
) -> Optional[QUERY_STATE]:
    logger.debug(f"Subscribing to query execution {query_execution_id}")
    if wait_for_states is None:
        wait_for_states = [QUERY_STATE.READY, QUERY_STATE.FAILED]
    try:
        async for update in client.query_execution_details(query_execution_id):
            if update.typedef_query_execution_by_pk:
                status = update.typedef_query_execution_by_pk.status
                logger.debug(
                    f"Subscription({query_execution_id}): Received state update: {status}."
                )
                if status in wait_for_states:
                    logger.debug("Exiting subscription")
                    return status
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return None


async def create_query_execution(
    client: Client,
    query_representation: str,
    user_id: UUID,
    parent_environment_id: UUID,
    parent_execution_session_id: UUID,
) -> Optional[UUID]:
    try:
        logger.debug(
            f"creating execution: query_representation: {query_representation}, user_id: {user_id}, parent_environment_id: {parent_environment_id}, parent_execution_session_id: {parent_execution_session_id}, client: {client}"
        )
        query_response = await client.create_query_execution(
            query_representation=query_representation,
            created_by_user_id=user_id,
            parent_environment_id=parent_environment_id,
            parent_execution_session_id=parent_execution_session_id,
        )
        resp = query_response.insert_typedef_query_execution.returning.pop()
        logger.debug(
            f"created execution: {resp.query_execution_id} in hasura.  resp: {resp}, user_id: {user_id}, parent_environment_id: {parent_environment_id}, parent_execution_session_id: {parent_execution_session_id}, query_representation: {query_representation}, client: {client}"
        )
        return resp.query_execution_id
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return None


async def update_query_execution_state(
    client: Client,
    query_execution_id: UUID,
    status: QUERY_STATE,
    error_code: int = 0,
    error_message: str = "",
) -> None:
    """
    Update the state of a query execution in the database.
    """
    query_execution = None
    try:
        query_response = await client.get_query_execution_details_by_id(
            query_execution_id
        )
        if len(query_response.typedef_query_execution) == 0:
            logger.debug("Query execution not found")
            return
        query_execution = query_response.typedef_query_execution.pop()
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
        return

    if query_execution.status == status and query_execution.error_code == error_code:
        logger.debug("Query execution already in this state")
        return

    try:
        if (
            status == QUERY_STATE.COMPLETED
            or status == QUERY_STATE.CANCELLED
            or status == QUERY_STATE.FAILED
        ):
            await client.update_query_execution_status_terminated(
                query_execution_id=query_execution_id,
                completed_at=datetime.now(),  # TODO: change schema to terminated_at
                status=status,
                error_code=error_code,
                error_message=error_message,
            )
        elif status == QUERY_STATE.RUNNING:
            await client.update_query_execution_status_running(
                query_execution_id=query_execution_id,
                submitted_at=datetime.now(),
            )
        else:
            await client.update_query_execution_status(
                query_execution_id=query_execution_id,
                status=status,
                error_code=error_code,
                error_message=error_message,
            )
    except GraphQLClientError as err:
        logger.debug(f"GraphQL caught exception: {err}")
