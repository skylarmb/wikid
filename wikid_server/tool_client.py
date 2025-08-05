#!/usr/bin/env python3
"""
Enhanced tool-aware client with streaming support for vLLM.
"""

import argparse
import json
import re
import sys
from openai import OpenAI
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown

from .tools import AVAILABLE_TOOLS, execute_tool_call

# Initialize rich console
console = Console()


def render_markdown(text: str) -> None:
    """Render markdown text using rich."""
    md = Markdown(text)
    console.print(md)


def print_assistant_response(content: str) -> None:
    """Print assistant response with markdown rendering."""
    print("Assistant: ", end="")
    render_markdown(content)


def create_client(base_url: str = "http://localhost:8000/v1", api_key: Optional[str] = None) -> OpenAI:
    """Create an OpenAI client for the vLLM server."""
    return OpenAI(
        base_url=base_url,
        api_key=api_key or "dummy-key"
    )


def parse_tool_calls_from_text(content: str) -> List[Dict[str, Any]]:
    """Parse tool calls from text content when they're not in structured format."""
    tool_calls = []
    
    # Debug: Log what we're parsing
    print(f"[DEBUG] Parsing tool calls from content ({len(content)} chars)")
    
    # Look for <tool_call> tags
    tool_call_pattern = r'<tool_call>\s*({.*?})\s*</tool_call>'
    matches = re.findall(tool_call_pattern, content, re.DOTALL)
    
    print(f"[DEBUG] Found {len(matches)} tool call matches")
    
    for i, match in enumerate(matches):
        try:
            tool_data = json.loads(match)
            tool_call = {
                'id': f'call_{i}',
                'function': {
                    'name': tool_data.get('name', ''),
                    'arguments': json.dumps(tool_data.get('arguments', {}))
                },
                'type': 'function'
            }
            tool_calls.append(tool_call)
            print(f"[DEBUG] Successfully parsed tool call: {tool_data.get('name', 'unknown')}")
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Warning: Failed to parse tool call: {match}")
            print(f"[DEBUG] JSON error: {e}")
    
    return tool_calls


def stream_response(response_stream):
    """Stream response content and collect it."""
    content = ""
    print("Assistant: ", end="", flush=True)
    
    for chunk in response_stream:
        if chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            content += chunk_content
            print(chunk_content, end="", flush=True)
    
    print()  # New line after streaming
    
    # Re-render the complete response with markdown formatting
    print("\nFormatted response:")
    render_markdown(content)
    
    return content


def chat_with_tools(
    client: OpenAI,
    message: str,
    model: str = "auto",
    max_tokens: int = 512,
    temperature: float = 0.7,
    tools: Optional[List[Dict]] = None,
    tool_choice: str = "auto",
    stream: bool = False,
) -> None:
    """Send a chat completion request with tools and handle function calls."""
    
    if tools is None:
        tools = AVAILABLE_TOOLS
    
    # Auto-detect model if not specified
    if model == "auto":
        try:
            models = client.models.list()
            if models.data:
                model = models.data[0].id
                print(f"[INFO] Using model: {model}")
            else:
                model = "default"  # Fallback
        except Exception:
            model = "default"  # Fallback if models endpoint fails
    
    # System prompt for the offline research assistant
    system_prompt = """You are an Arch Linux documentation assistant with access to the Arch Linux Wiki via ZIM files.

CRITICAL: You are responding to users, not showing internal thoughts. Give clean, helpful responses with proper citations.

ABSOLUTE REQUIREMENTS:
- Never include your reasoning process in the final response
- Never explain what you're thinking or planning to do
- Provide direct, useful answers to user questions  
- Focus only on English content from the Arch Linux Wiki
- Skip any foreign language content (French, German, etc.)
- ALWAYS cite your sources by naming the wiki pages you used

Available tools: search_zim, get_zim_entry, list_zim_files, get_zim_suggestions

RESPONSE FORMAT:
1. Use tools silently (thinking is private)
2. After getting results, provide a clean user-facing answer
3. Extract useful English content only
4. Always end responses with "Sources: [Page Name 1], [Page Name 2]" format
5. Be helpful and concise

EXAMPLES:
User: "How do I install packages?"
Your response: "Use pacman to install packages: 'pacman -S package_name'. This installs the specified package and its dependencies from the official repositories.

Sources: Package management, Pacman"

User: "Show me documentation about systemd"
Your response: "systemd is a system and service manager for Linux operating systems. It is the default init system for Arch Linux and provides parallel startup of system services.

Sources: systemd"

CITATION RULES:
- Always include "Sources: " followed by page names
- Use exact wiki page titles from your search results
- If you use multiple pages, list them separated by commas
- If no sources were used (rare), write "Sources: None"

Your thinking happens privately. Your response includes proper citations."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    
    print(f"User: {message}")
    print("-" * 50)
    
    # Initial request
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        tools=tools,
        tool_choice=tool_choice,
        stream=stream,
    )
    
    if stream:
        # Handle streaming response
        assistant_content = stream_response(response)
    else:
        # Handle non-streaming response
        assistant_message = response.choices[0].message
        assistant_content = assistant_message.content
        print_assistant_response(assistant_content)
    
    # Check for tool calls in the content
    tool_calls = parse_tool_calls_from_text(assistant_content)
    
    # Debug: Log tool call detection
    print(f"\n[DEBUG] Tool calls detected: {len(tool_calls)}")
    if len(tool_calls) > 0:
        print(f"[DEBUG] Tool call details: {[tc['function']['name'] for tc in tool_calls]}")
    
    if tool_calls:
        print("\n" + "=" * 20 + " TOOL CALLS " + "=" * 20)
        
        # Add assistant message to conversation
        messages.append({
            "role": "assistant", 
            "content": assistant_content,
            "tool_calls": tool_calls
        })
        
        for i, tool_call in enumerate(tool_calls, 1):
            # Handle parsed tool calls
            tool_name = tool_call['function']['name']
            tool_args = json.loads(tool_call['function']['arguments'])
            tool_call_id = tool_call['id']
            
            print(f"\n[{i}] Calling tool: {tool_name}")
            print(f"    Arguments: {tool_args}")
            print(f"    Tool call ID: {tool_call_id}")
            
            # Execute the tool
            try:
                tool_result = execute_tool_call(tool_name, tool_args)
                print(f"    Result length: {len(str(tool_result))} characters")
                # Show first 200 chars of result for logging
                result_preview = str(tool_result)[:200] + "..." if len(str(tool_result)) > 200 else str(tool_result)
                print(f"    Result preview: {result_preview}")
            except Exception as e:
                print(f"    ERROR: Tool execution failed: {e}")
                tool_result = f"Error executing tool: {e}"
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call_id
            })
        
        # Get final response with tool results
        print("\n" + "-" * 15 + " FINAL RESPONSE " + "-" * 15)
        
        final_response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )
        
        if stream:
            stream_response(final_response)
        else:
            final_content = final_response.choices[0].message.content
            print_assistant_response(final_content)


def interactive_mode(client: OpenAI, model: str, max_tokens: int, temperature: float, 
                    tool_choice: str, stream: bool):
    """Run in interactive mode for continuous conversation."""
    print("Wikid Chat - Interactive Mode")
    print("Type 'quit', 'exit', or press Ctrl+C to exit")
    print("Type '/tools' to list available tools")
    print("Type '/stream' to toggle streaming mode")
    print("=" * 60)
    
    try:
        while True:
            try:
                message = input("\nYou: ").strip()
                
                if message.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if message == '/tools':
                    print("\nAvailable tools:")
                    for tool in AVAILABLE_TOOLS:
                        func = tool["function"]
                        print(f"* {func['name']}: {func['description']}")
                    continue
                
                if message == '/stream':
                    stream = not stream
                    print(f"Streaming mode: {'ON' if stream else 'OFF'}")
                    continue
                
                if not message:
                    continue
                
                chat_with_tools(
                    client, message, model, max_tokens, temperature,
                    tool_choice=tool_choice, stream=stream
                )
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
    except Exception as e:
        print(f"\nError in interactive mode: {e}")


def main():
    """Main entry point for the enhanced tool client."""
    parser = argparse.ArgumentParser(
        description="Interactive tool-aware client with streaming support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wikid-chat                       # Start interactive mode with streaming
  wikid-chat "Hello world"         # One-shot mode (non-streaming)
  wikid-chat --no-stream           # Interactive mode without streaming  
  wikid-chat --list-tools          # List available tools
        """)
    parser.add_argument(
        "message",
        nargs="?",
        help="Message for one-shot mode (if provided, runs in non-streaming mode and exits)"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000/v1",
        help="Base URL for the vLLM server (default: %(default)s)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    parser.add_argument(
        "--model",
        default="auto",
        help="Model name (default: auto-detect from server)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens in response (default: %(default)s)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for sampling (default: %(default)s)"
    )
    parser.add_argument(
        "--tool-choice",
        default="auto",
        choices=["auto", "none", "required"],
        help="Tool choice mode (default: %(default)s)"
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses (streaming is default)"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_tools:
        print("Available Tools:")
        print("=" * 60)
        for tool in AVAILABLE_TOOLS:
            func = tool["function"]
            print(f"\n[{func['name']}]")
            print(f"   {func['description']}")
            print(f"   Parameters: {', '.join(func['parameters']['required']) if 'required' in func['parameters'] else 'None'}")
        return
    
    try:
        client = create_client(args.base_url, args.api_key)
        
        if args.message:
            # One-shot mode (always non-streaming)
            chat_with_tools(
                client, args.message, args.model, args.max_tokens, 
                args.temperature, tool_choice=args.tool_choice, stream=False
            )
        else:
            # Interactive mode
            # Streaming is enabled by default, disabled with --no-stream
            stream_enabled = not args.no_stream
            
            interactive_mode(client, args.model, args.max_tokens, 
                            args.temperature, args.tool_choice, stream_enabled)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()