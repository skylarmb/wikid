#!/usr/bin/env python3
"""
Sample tools for testing MCP/function calling with vLLM.
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any

from .zim_tools import search_zim, get_zim_entry, list_zim_files, get_zim_suggestions


def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Get the current weather for a specified location.
    
    Args:
        location: The city and state/country, e.g. "San Francisco, CA"
        unit: Temperature unit, either "celsius" or "fahrenheit"
    
    Returns:
        Weather information as a JSON string
    """
    # Mock weather data
    weather_conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "windy"]
    temperature_c = random.randint(-10, 35)
    
    if unit == "fahrenheit":
        temperature = (temperature_c * 9/5) + 32
        temp_unit = "°F"
    else:
        temperature = temperature_c
        temp_unit = "°C"
    
    weather = {
        "location": location,
        "temperature": f"{temperature}{temp_unit}",
        "condition": random.choice(weather_conditions),
        "humidity": f"{random.randint(30, 90)}%",
        "wind_speed": f"{random.randint(5, 25)} km/h",
        "timestamp": datetime.now().isoformat()
    }
    
    return json.dumps(weather, indent=2)


def calculate_math(expression: str) -> str:
    """
    Calculate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2 * 3")
    
    Returns:
        Result of the calculation
    """
    try:
        # Only allow basic math operations for safety
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations (+, -, *, /, parentheses) are allowed"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time in a specified timezone.
    
    Args:
        timezone: Timezone (currently only supports UTC)
    
    Returns:
        Current time information
    """
    now = datetime.now()
    
    time_info = {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": timezone,
        "day_of_week": now.strftime("%A"),
        "timestamp": now.timestamp()
    }
    
    return json.dumps(time_info, indent=2)




# Tool definitions for OpenAI function calling format
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_zim",
            "description": "Search for content across offline ZIM knowledge bases (Wikipedia, Stack Exchange, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "zim_file": {
                        "type": "string",
                        "description": "Optional specific ZIM file to search (filename)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_zim_entry",
            "description": "Retrieve a specific article or page from ZIM knowledge bases",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the article to retrieve"
                    },
                    "zim_file": {
                        "type": "string",
                        "description": "Optional specific ZIM file to search (filename)"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_zim_files",
            "description": "List all available offline knowledge bases (ZIM files)",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_zim_suggestions",
            "description": "Get search suggestions for better discovery of topics",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to get suggestions for"
                    },
                    "zim_file": {
                        "type": "string",
                        "description": "Optional specific ZIM file to search (filename)"
                    },
                    "max_suggestions": {
                        "type": "integer",
                        "description": "Maximum number of suggestions to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (currently only supports UTC)",
                        "default": "UTC"
                    }
                }
            }
        }
    }
]


def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool call by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
    
    Returns:
        Result of the tool execution
    """
    tool_functions = {
        "search_zim": search_zim,
        "get_zim_entry": get_zim_entry,
        "list_zim_files": list_zim_files,
        "get_zim_suggestions": get_zim_suggestions,
        "get_current_time": get_current_time,
    }
    
    if tool_name not in tool_functions:
        return f"Error: Unknown tool '{tool_name}'"
    
    try:
        func = tool_functions[tool_name]
        result = func(**arguments)
        return result
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"


if __name__ == "__main__":
    # Test the tools
    print("Testing weather tool:")
    print(get_current_weather("San Francisco, CA", "fahrenheit"))
    
    print("\nTesting math tool:")
    print(calculate_math("2 + 2 * 3"))
    
    print("\nTesting time tool:")
    print(get_current_time())