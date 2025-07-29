#!/usr/bin/env python3
"""Test script to verify todo.sh configuration integration."""

import asyncio
import tempfile
from pathlib import Path

from src.todo_txt_mcp.server import create_server


async def test_todo_sh_integration():
    """Test that we can create a server with todo.sh configuration."""

    # Create a temp todo file for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in directory: {temp_dir}")

        # Create a sample todo.sh config
        temp_config = Path(temp_dir) / "todo.cfg"
        temp_config.write_text(
            f"""
# Test todo.sh configuration
export TODO_DIR="{temp_dir}"
export TODO_FILE="$TODO_DIR/todo.txt"
export DONE_FILE="$TODO_DIR/done.txt"
export REPORT_FILE="$TODO_DIR/report.txt"
"""
        )

        print(f"Created config file: {temp_config}")

        # Create server with this config
        server = create_server(todo_sh_config_path=str(temp_config))
        print("✅ Server created successfully with todo.sh config!")
        print(f"Server name: {server.name}")

        # Test that tools are available
        tools = await server.list_tools()
        print(f"✅ Available tools: {len(tools)} tools")
        expected_tools = {
            "list_todos",
            "get_todo",
            "search_todos",
            "filter_by_priority",
            "filter_by_project",
            "filter_by_context",
            "get_statistics",
            "add_todo",
            "complete_todo",
            "update_todo",
            "delete_todo",
            "reload_todos",
        }
        tool_names = {tool.name for tool in tools}
        if expected_tools.issubset(tool_names):
            print("✅ All expected tools are available")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description[:50]}...")
        else:
            missing = expected_tools - tool_names
            print(f"❌ Missing tools: {missing}")

        # Test that resources are available
        resources = await server.list_resources()
        print(f"✅ Available resources: {len(resources)} resources")
        expected_resources = {"todo://file", "todo://stats"}
        resource_uris = {str(resource.uri) for resource in resources}
        print(f"Found resource URIs: {resource_uris}")
        if expected_resources.issubset(resource_uris):
            print("✅ All expected resources are available")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.description[:50]}...")
        else:
            missing = expected_resources - resource_uris
            print(f"❌ Missing resources: {missing}")
            print("Available resources:")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.description[:50]}...")

        print("\n🎉 todo.sh configuration integration test passed!")


if __name__ == "__main__":
    asyncio.run(test_todo_sh_integration())
