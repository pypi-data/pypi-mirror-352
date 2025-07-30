from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import Runnable
import re
from pydantic import TypeAdapter
from .models import ToolCall

class ManualToolAgent(Runnable):
    """
    A custom agent that handles tools manually.
    """
    def __init__(self, model, tools):
        self.model = model
        self.tools = tools
        self.json_parser = JsonOutputParser(pydantic_object=ToolCall)
        self.base_executor = create_react_agent(model, tools=[])
        self.max_retries = 100
    
    def convert_messages(self, messages: List[dict]) -> List[SystemMessage | HumanMessage | AIMessage]:
        """
        Convert dictionary-based messages to LangChain message objects.
        """
        converted_messages = []
        
        message_types = {
            "system": SystemMessage,
            "user": HumanMessage,
            "assistant": AIMessage
        }
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role in message_types:
                MessageClass = message_types[role]
                converted_message = MessageClass(content=content)
                converted_messages.append(converted_message)
                
        return converted_messages
    
    def is_empty_response(self, response_text: str) -> bool:
        """
        Check if the response is empty or contains only whitespace.
        
        Args:
            response_text (str): The response text to check
            
        Returns:
            bool: True if response is empty, False otherwise
        """
        if response_text is None:
            return True
        if not response_text.strip():
            return True
        return False
    
    def format_tool_result(self, tool_name: str, tool_result: str, user_query: str) -> str:
        """
        Format tool result using LLM to create natural language response.
        """
        prompt = f"""Given the following:
                     User query: {user_query}
                     Tool used: {tool_name}
                     Tool result: {tool_result}

                     Create a natural language response to the "User query" that incorporates the result from the "Tool result". DO NOT mention anything about using OR not using the tool or tools mentioned in "Tool used" or "Tool result". 
                     Only provide this natural language response and keep it concise and direct WITHOUT mentioning anything about the tool or tools mentioned in "Tool used" or "Tool result."""
        
        retry_count = 0
        while retry_count < self.max_retries:
            response = self.model.invoke([HumanMessage(content=prompt)])
            
            # Check if model is ChatBedrockConverse by class name
            if type(self.model).__name__ == "ChatBedrockConverse":
                response_content = response.content[0]['text']
            else:
                response_content = response.content
                
            if not self.is_empty_response(response_content):
                return response_content
            retry_count += 1
        
        # If we've reached here, we've exceeded max retries with empty responses
        # Return a default response with the raw tool result
        return f"The result is: {tool_result}"
    
    def invoke(self, inputs: dict) -> dict:
        """
        Execute the agent with manual tool handling.
        
        Args:
            inputs (dict): Dictionary containing messages
            
        Returns:
            dict: Response containing processed message
        """
        # Get messages
        messages = inputs["messages"]
        user_query = messages[-1]["content"]  # Get the last user message
        
        # Convert messages to LangChain format
        converted_formatted_messages = self.convert_messages(messages)
        
        # Get response from base executor with retry logic for empty responses
        last_response = None
        retry_count = 0
        while retry_count < self.max_retries:
            response = self.base_executor.invoke({"messages": converted_formatted_messages})
            
            # Check if model is ChatBedrockConverse by class name
            if type(self.model).__name__ == "ChatBedrockConverse":
                last_response = response["messages"][-1].content[0]['text']
            else:
                last_response = response["messages"][-1].content
            
            if not self.is_empty_response(last_response):
                break
                
            retry_count += 1
            
        # If we still have an empty response after all retries, return an error message
        if self.is_empty_response(last_response):
            return {"messages": [{"content": "I'm having trouble generating a response. Please try again."}]}
        
        # Process JSON response
        matches = re.findall(r'(\{.*?\})', last_response, re.DOTALL)
        json_text = None
        for m in matches:
            if '"tool"' in m and '"args"' in m:
                json_text = m
                break
        
        if json_text:
            try:
                adapter = TypeAdapter(ToolCall)
                parsed = self.json_parser.parse(json_text)
                
                if isinstance(parsed, dict):
                    tool_call = adapter.validate_python(parsed)
                else:
                    tool_call = parsed
                
                # Find the matching tool
                tool_dict = {tool.name: tool for tool in self.tools}
                
                if tool_call.tool in tool_dict:
                    raw_result = tool_dict[tool_call.tool].invoke(tool_call.args)
                    # Format the result using LLM
                    result = self.format_tool_result(tool_call.tool, raw_result, user_query)
                else:
                    result = "Error: Unknown tool"
            except Exception as e:
                result = f"Error processing tool call: {str(e)}"
        else:
            result = last_response
        
        return {"messages": [{"content": result}]}

def create_react_agent_taot(model, tools) -> ManualToolAgent:
    """
    Create a React agent with manual tool handling.
    
    Args:
        model: The language model to use
        tools (List): List of tool functions
        
    Returns:
        ManualToolAgent: Agent with manual tool handling
    """
    return ManualToolAgent(model, tools)