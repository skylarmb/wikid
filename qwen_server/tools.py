#!/usr/bin/env python3
"""
Sample tools for testing MCP/function calling with vLLM.
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any


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
            "name": "get_current_weather",
            "description": "Get the current weather for a specified location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state/country, e.g. 'San Francisco, CA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "Calculate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 2 * 3')"
                    }
                },
                "required": ["expression"]
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
        "get_current_weather": get_current_weather,
        "calculate_math": calculate_math,
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