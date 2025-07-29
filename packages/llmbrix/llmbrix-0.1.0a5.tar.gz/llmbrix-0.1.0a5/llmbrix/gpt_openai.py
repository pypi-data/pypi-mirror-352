from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall
from pydantic import BaseModel

from llmbrix.msg import AssistantMsg, Msg, ToolRequestMsg
from llmbrix.tool import Tool

client = OpenAI()


class GptResponse(BaseModel):
    message: AssistantMsg
    tool_calls: list[ToolRequestMsg]


class GptOpenAI:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()

    def generate(self, messages: list[Msg], tools: list[Tool] = None) -> GptResponse:
        messages = [m.to_openai() for m in messages]
        if tools is not None:
            tools = [t.openai_schema for t in tools]
        else:
            tools = []
        response = self.client.responses.create(input=messages, model=self.model, tools=tools)
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API cal: "
                f"code={response.error}, "
                f'msg="{response.error.message}"'
            )
        tool_call_requests = [
            ToolRequestMsg.from_openai(t)
            for t in response.output
            if isinstance(t, ResponseFunctionToolCall)
        ]
        return GptResponse(
            message=AssistantMsg(content=response.output_text), tool_calls=tool_call_requests
        )

    def generate_structured(
        self, messages: list[Msg], output_format: BaseModel
    ) -> BaseModel | None:
        messages = [m.to_openai() for m in messages]
        response = self.client.responses.parse(
            input=messages, model=self.model, text_format=output_format
        )
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API cal: "
                f"code={response.error}, "
                f'msg="{response.error.message}"'
            )
        return response.output_parsed
