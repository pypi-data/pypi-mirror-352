from typing import Literal, Optional

from pydantic import Field
from pydantic.types import UUID4

from galileo_core.schemas.logging.step import BaseStep, StepType


class Session(BaseStep):
    type: Literal[StepType.session] = Field(
        default=StepType.session, description=BaseStep.model_fields["type"].description
    )
    previous_session_id: Optional[UUID4] = None
