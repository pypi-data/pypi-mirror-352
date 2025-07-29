# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
|---------|--------------------|
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Todo.txt MCP Server team takes security bugs seriously. We appreciate your efforts to responsibly disclose your
findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **pilots-4-trilogy@icloud.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we
received your original message.

### What to Include

When reporting a vulnerability, please include the following information:

- **Type of issue** (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- **Full paths of source file(s) related to the manifestation of the issue**
- **The location of the affected source code** (tag/branch/commit or direct URL)
- **Any special configuration required to reproduce the issue**
- **Step-by-step instructions to reproduce the issue**
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit the issue

### Preferred Languages

We prefer all communications to be in English.

## Security Considerations

### Local File Access

This MCP server operates on local files and has the following security characteristics:

1. **File Access Scope**: The server only accesses todo.txt files as configured
2. **No Network Access**: The server does not make external network requests
3. **Local Execution**: All operations are performed locally
4. **Input Validation**: User inputs are validated to prevent injection attacks
5. **File Size Limits**: Configurable limits prevent resource exhaustion

### MCP Security Model

As an MCP server, this project:

- **Runs locally**: Does not expose services to external networks
- **Client-controlled**: Only responds to authenticated MCP clients
- **Sandboxed operations**: File operations are limited to configured directories
- **No privilege escalation**: Runs with user-level permissions only

### Deployment Recommendations

For secure deployment:

1. **Use specific file paths**: Configure exact paths rather than wildcards
2. **Regular updates**: Keep the package updated to the latest version
3. **Access control**: Ensure todo.txt files have appropriate file permissions
4. **Environment isolation**: Consider using virtual environments for Python packages

### Known Security Considerations

1. **File System Access**: The server can read/write files within configured directories
2. **Todo.txt Content**: The server processes todo.txt content which could contain user data
3. **Configuration Files**: Claude Desktop configuration may contain sensitive paths

## Vulnerability Response Process

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Investigation**: Our team will investigate and validate the reported vulnerability
3. **Timeline**: We aim to provide an initial assessment within 5 business days
4. **Resolution**: Critical vulnerabilities will be addressed in emergency releases
5. **Disclosure**: We will coordinate with you on responsible disclosure timing

## Security Updates

- Security updates will be released as patch versions
- Critical security issues may result in immediate releases outside normal schedule
- Security advisories will be published on GitHub Security Advisories
- Users will be notified via release notes and GitHub notifications

## Best Practices for Users

### Installation Security

```bash
# Verify package integrity before installation
pip install --user todo-txt-mcp

# Use virtual environments to isolate dependencies
uv venv
uv install todo-txt-mcp
```

### Configuration Security

```json
{
    "mcpServers": {
        "todo-txt": {
            "command": "uv",
            "args": [
                "run",
                "todo-txt-mcp",
                "/specific/path/to/todo.txt"
            ],
            "env": {
                "TODO_MCP_MAX_FILE_SIZE": "1000000"
            }
        }
    }
}
```

### File System Security

- Use specific file paths rather than directory access
- Set appropriate file permissions on todo.txt files
- Regularly backup your todo.txt files
- Monitor for unexpected file changes

## Third-Party Dependencies

We regularly audit our dependencies for security vulnerabilities:

- **Automated scanning**: GitHub Dependabot alerts
- **Regular updates**: Dependencies are updated regularly
- **Minimal dependencies**: We keep the dependency tree small
- **Trusted sources**: Only use dependencies from trusted maintainers

## Contact

For general security questions or concerns, please email: pilots-4-trilogy@icloud.com

For urgent security matters, please include "[URGENT SECURITY]" in the email subject line.

---

Thank you for helping keep Todo.txt MCP Server and our users safe! 
