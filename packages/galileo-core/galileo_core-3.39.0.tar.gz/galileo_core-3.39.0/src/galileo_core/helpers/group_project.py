from typing import Optional

from pydantic import UUID4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes
from galileo_core.helpers.logger import logger
from galileo_core.schemas.base_config import GalileoConfig
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.group_project import GroupProjectCollaboratorRequest, GroupProjectCollaboratorResponse


def share_project_with_group(
    project_id: UUID4,
    group_id: UUID4,
    role: CollaboratorRole = CollaboratorRole.viewer,
    config: Optional[GalileoConfig] = None,
) -> GroupProjectCollaboratorResponse:
    config = config or GalileoConfig.get()
    logger.debug(f"Sharing project {project_id} with group {group_id} with role {role}...")
    response_dict = config.api_client.request(
        RequestMethod.POST,
        Routes.project_groups.format(project_id=project_id),
        json=[GroupProjectCollaboratorRequest(group_id=group_id, role=role).model_dump(mode="json")],
    )
    group_collaborators = [GroupProjectCollaboratorResponse.model_validate(group) for group in response_dict]
    logger.debug(f"Shared project {project_id} with group {group_id} with role {role}.")
    return group_collaborators[0]


def unshare_project_with_group(
    project_id: UUID4,
    group_id: UUID4,
    config: Optional[GalileoConfig] = None,
) -> None:
    config = config or GalileoConfig.get()
    logger.debug(f"Removing access for group {group_id} from project {project_id}")
    config.api_client.request(
        RequestMethod.DELETE, Routes.project_group.format(project_id=project_id, group_id=group_id)
    )
    logger.debug(f"Access for group {group_id} removed from project {project_id}.")
