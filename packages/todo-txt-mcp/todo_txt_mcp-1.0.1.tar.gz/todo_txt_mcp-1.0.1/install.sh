#!/bin/bash

# Todo.txt MCP Server - Quick Install Script
# Usage: curl -sSL https://raw.githubusercontent.com/danielmeint/todo-txt-mcp/main/install.sh | bash

set -e

echo "🚀 Installing Todo.txt MCP Server..."

# Check if uv is available (preferred)
if command -v uv >/dev/null 2>&1; then
    echo "✅ Found uv, installing with uv tool..."
    uv tool install todo-txt-mcp
    echo "✅ Installation complete! You can now run: todo-txt-mcp"
# Check if pipx is available (second choice)
elif command -v pipx >/dev/null 2>&1; then
    echo "✅ Found pipx, installing with pipx..."
    pipx install todo-txt-mcp
    echo "✅ Installation complete! You can now run: todo-txt-mcp"
# Fall back to pip
elif command -v pip >/dev/null 2>&1; then
    echo "⚠️  Using pip (consider installing uv or pipx for better isolation)..."
    pip install --user todo-txt-mcp
    echo "✅ Installation complete! You can now run: todo-txt-mcp"
    echo "💡 If 'todo-txt-mcp' is not found, add ~/.local/bin to your PATH"
else
    echo "❌ No Python package manager found (pip, pipx, or uv required)"
    echo "Please install Python and pip, then run: pip install todo-txt-mcp"
    exit 1
fi

echo ""
echo "📝 Next steps:"
echo "1. Add to Claude Desktop config:"
echo '   {' 
echo '     "mcpServers": {'
echo '       "todo-txt": {'
echo '         "command": "uvx",'
echo '         "args": ["todo-txt-mcp"]'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "2. Restart Claude Desktop"
echo "3. Look for the 🔨 tools icon in Claude"
echo ""
echo "📖 Full documentation: https://github.com/danielmeint/todo-txt-mcp"
echo "🎉 Happy todo management with AI!" 