from langchain_core.output_parsers import JsonOutputParser
from .models import ToolCall

def create_system_message_taot(system_message: str) -> str:
    """
    Create a system message with tool instructions and JSON schema.
    
    Args:
        system_message (str): The specific system message for tools
        
    Returns:
        str: Formatted system message with JSON schema instructions
    """
    json_parser = JsonOutputParser(pydantic_object=ToolCall)
    
    sys_msg_taot = (f"{system_message}\n"
                    f"Firstly, check if the user's question matches a tool's capability. "
                    f"When a user's question matches a tool's capability, you MUST use that tool.\n "
                    f"When a tool is being used, output ONLY a JSON object (with no extra text) that adheres EXACTLY to the following schema:\n\n"
                    f"{json_parser.get_format_instructions()}\n\n"
                    f"Secondly, after checking if the user's question does not match a tool's capability, then answer directly in plain text with no JSON.\n"
                    f"DO NOT try to solve problems manually if a tool exists for that purpose.")

    return sys_msg_taot