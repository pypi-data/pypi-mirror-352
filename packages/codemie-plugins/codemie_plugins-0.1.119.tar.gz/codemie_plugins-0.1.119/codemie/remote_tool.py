from typing import Optional, Callable

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from codemie.logging import logger
import asyncio
import json
import uuid
from .util.term_util import format_tool_message


class RemoteTool(BaseModel):
    tool: BaseTool
    subject: str
    tool_result_converter: Optional[Callable[[ToolMessage], str]] = None

    def tool_schema(self):
        return {
            "name": self.tool.name,
            "subject": self.subject,
            "description": self.tool.description,
            "args_schema": self.tool.args_schema
        }

    async def execute_tool_with_timeout(self, query, timeout):
        error_message = "Call to the tool timed out."
        try:
            tool_input = json.loads(query)
            tool_response = await asyncio.wait_for(
                self.tool.arun(tool_input, tool_call_id=str(uuid.uuid4())), timeout
            )
            logger.info(format_tool_message(self.tool.name, tool_input, tool_response))
            return tool_response

        except asyncio.TimeoutError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' operation timed out after {timeout} seconds\n{separator}"
            logger.error(error_msg)
            return error_message
        except json.JSONDecodeError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' failed to decode JSON input\n{separator}"
            logger.error(error_msg)
            return "Failed to decode JSON input."
        except Exception as e:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' error: {e}\n{separator}"
            logger.error(error_msg)
            return f"An error occurred: {e}"