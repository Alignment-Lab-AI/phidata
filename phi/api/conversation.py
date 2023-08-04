from typing import Optional

from phi.api.client import api_client, invalid_response
from phi.api.routes import ApiRoutes
from phi.api.schemas.monitor import ConversationEventSchema, ConversationResponseSchema
from phi.api.schemas.workspace import WorkspaceSchema
from phi.cli.settings import phi_cli_settings
from phi.utils.log import logger


async def log_conversation_event(monitor: ConversationEventSchema, workspace: WorkspaceSchema) -> Optional[ConversationResponseSchema]:
    if not phi_cli_settings.api_enabled:
        return None

    logger.debug("--o-o-- Log conversation event")
    try:
        async with api_client.Session() as api:
            async with api.post(
                ApiRoutes.CONVERSATION_EVENT,
                json={
                    "monitor": monitor.model_dump(exclude_none=True),
                    "workspace": workspace.model_dump(include={"id_workspace"}),
                },
            ) as response:
                if invalid_response(response):
                    return None

                response_json = await response.json()
                if response_json is None:
                    return None

                # logger.info(response_json)
                try:
                    monitor_response: ConversationResponseSchema = ConversationResponseSchema.model_validate(response_json)
                    if monitor_response is not None:
                        return monitor_response
                    return None
                except Exception as e:
                    logger.warning(e)
    except Exception as e:
        logger.debug(f"Could not log monitor event: {e}")
    return None
