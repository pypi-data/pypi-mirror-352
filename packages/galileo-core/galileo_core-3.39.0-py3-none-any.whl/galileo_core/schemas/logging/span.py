import math
from json import dumps
from typing import Any, Dict, List, Literal, Optional, Sequence, Union, cast

from pydantic import ConfigDict, Field, field_validator
from pydantic_core import ValidationError
from typing_extensions import Annotated

from galileo_core.schemas.logging.llm import Message, MessageRole
from galileo_core.schemas.logging.step import BaseStep, Metrics, StepAllowedInputType, StepType
from galileo_core.schemas.shared.document import Document
from galileo_core.utils.json import PydanticJsonEncoder

LlmSpanAllowedInputType = Union[Sequence[Message], Message, str, Dict[str, Any], Sequence[Dict[str, Any]]]
LlmSpanAllowedOutputType = Union[Message, str, Dict[str, Any]]


class BaseSpan(BaseStep):
    input: StepAllowedInputType = Field(description="Input to the trace or span.")


class StepWithChildSpans(BaseSpan):
    spans: List["Span"] = Field(default_factory=list, description="Child spans.")

    def add_child_spans(self, spans: Sequence["Span"]) -> None:
        self.spans.extend(spans)

    def add_child_span(self, span: "Span") -> None:
        self.add_child_spans([span])


class BaseWorkflowSpan(BaseSpan):
    type: Literal[StepType.workflow] = Field(
        default=StepType.workflow, description=BaseStep.model_fields["type"].description
    )


class WorkflowSpan(BaseWorkflowSpan, StepWithChildSpans):
    pass


class LlmMetrics(Metrics):
    num_input_tokens: Optional[int] = Field(default=None, description="Number of input tokens.")
    num_output_tokens: Optional[int] = Field(default=None, description="Number of output tokens.")
    num_total_tokens: Optional[int] = Field(default=None, description="Total number of tokens.")
    time_to_first_token_ns: Optional[int] = Field(
        default=None,
        description="Time until the first token was generated in nanoseconds.",
    )

    model_config = ConfigDict(extra="allow")


class LlmSpan(BaseSpan):
    type: Literal[StepType.llm] = Field(default=StepType.llm, description=BaseStep.model_fields["type"].description)
    input: Sequence[Message] = Field(description=BaseStep.model_fields["input"].description)
    output: Message = Field(description=BaseStep.model_fields["output"].description)
    metrics: LlmMetrics = Field(default_factory=LlmMetrics, description=BaseStep.model_fields["metrics"].description)
    tools: Optional[Sequence[Dict[str, Any]]] = Field(
        default=None,
        description="List of available tools passed to the LLM on invocation.",
    )
    model: Optional[str] = Field(default=None, description="Model used for this span.")
    temperature: Optional[float] = Field(default=None, description="Temperature used for generation.")
    finish_reason: Optional[str] = Field(default=None, description="Reason for finishing.")

    @classmethod
    def _convert_dict_to_message(cls, value: Dict[str, Any], default_role: MessageRole = MessageRole.user) -> Message:
        """
        Converts a dict into a Message object.
        Will dump the dict to a json string if it unable to be deserialized into a Message object.

        Args:
            value (Dict[str, Any]): The dict to convert.
            default_role (Optional[MessageRole], optional): The role to use if the dict does not contain a role. Defaults to MessageRole.user.

        Returns:
            Message: The converted Message object.
        """
        try:
            return Message.model_validate(value)
        except ValidationError:
            return Message(content=dumps(value), role=default_role)

    @field_validator("tools", mode="after")
    def validate_tools_serializable(cls, val: Optional[Sequence[Dict[str, Any]]]) -> Optional[Sequence[Dict[str, Any]]]:
        # Make sure we can dump input/output to json string.
        dumps(val, cls=PydanticJsonEncoder)
        return val

    @field_validator("input", mode="before")
    def convert_input(cls, value: LlmSpanAllowedInputType) -> Sequence[Message]:
        """Converts various input types into a standardized list of Message objects."""
        if isinstance(value, Sequence) and all(isinstance(item, Message) for item in value):
            return cast(Sequence[Message], value)
        if isinstance(value, Sequence) and all(isinstance(item, Dict) for item in value):
            return [
                cls._convert_dict_to_message(value=cast(Dict[str, Any], item), default_role=MessageRole.user)
                for item in value
            ]
        if isinstance(value, str):
            return [Message(role=MessageRole.user, content=value)]
        if isinstance(value, Message):
            return [value]
        if isinstance(value, Dict):
            return [cls._convert_dict_to_message(value=value, default_role=MessageRole.user)]
        raise ValueError("LLM span input must be a Message, a list of Messages, a dict, a list of dicts, or a string.")

    @field_validator("output", mode="before")
    def convert_output(cls, value: LlmSpanAllowedOutputType) -> Message:
        """Converts various output types into a standardized Message object."""
        if isinstance(value, Message):
            return value
        if isinstance(value, str):
            return Message(role=MessageRole.assistant, content=value)
        if isinstance(value, Dict):
            return cls._convert_dict_to_message(value=value, default_role=MessageRole.assistant)
        raise ValueError("LLM span output must be a Message, a string, or a dict.")

    @field_validator("temperature", mode="before")
    def convert_temperature(cls, value: Optional[float]) -> Optional[float]:
        if value is None or math.isnan(value) or math.isinf(value):
            return None
        return value


class RetrieverSpan(BaseSpan):
    type: Literal[StepType.retriever] = Field(
        default=StepType.retriever, description=BaseStep.model_fields["type"].description
    )
    input: str = Field(description=BaseStep.model_fields["input"].description)
    output: List[Document] = Field(description=BaseStep.model_fields["output"].description)

    @field_validator("output", mode="before")
    def set_output(cls, value: Union[List[Dict[str, str]], List[Document]]) -> List[Document]:
        if isinstance(value, list):
            if all(isinstance(doc, dict) for doc in value):
                parsed = [Document.model_validate(doc) for doc in value]
            elif all(isinstance(doc, Document) for doc in value):
                parsed = [Document.model_validate(doc) for doc in value]
            else:
                raise ValueError("Retriever output must be a list of dicts, or a list of Documents.")
            return parsed
        raise ValueError("Retriever output must be a list of dicts or a list of Documents.")


class ToolSpan(BaseSpan):
    type: Literal[StepType.tool] = Field(default=StepType.tool, description=BaseStep.model_fields["type"].description)
    input: str = Field(description=BaseStep.model_fields["input"].description)
    output: Optional[str] = Field(default=None, description=BaseStep.model_fields["output"].description)
    tool_call_id: Optional[str] = Field(default=None, description="ID of the tool call.")


Span = Annotated[Union[WorkflowSpan, LlmSpan, RetrieverSpan, ToolSpan], Field(discriminator="type")]

StepWithChildSpans.model_rebuild()

SpanStepTypes = [step_type.value for step_type in StepType if step_type != StepType.trace]
