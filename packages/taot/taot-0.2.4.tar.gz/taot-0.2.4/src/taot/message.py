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
    
    sys_msg_taot = (f"{system_message}\n\n"
                    f"IMPORTANT INSTRUCTIONS:\n"
                    f"- If the user's question requires using one of your available tools, respond with ONLY a JSON object (no additional text) that follows this exact schema:\n\n"
                    f"{json_parser.get_format_instructions()}\n\n"
                    f"- If the user's question does not require any tools, respond directly with a natural answer in plain text.\n"
                    f"- Never explain whether or not you are using tools.\n"
                    f"- Never include reasoning about tool selection in your response.\n"
                    f"- Do not attempt to solve problems manually if an appropriate tool exists.")

    return sys_msg_taot