# SSH MCP Server

A Machine Control Protocol (MCP) server that provides tools for LLMs to safely SSH into remote dev/test machines. 

## Features

- SSH connection management to remote machines
- Run query scripts for retrieving information
- Cautiously run modifying scripts for debugging purposes
- Secure credential management using SSH key authentication

## Tools

### run_query_script
Executes read-only shell scripts on remote machines to gather information without modifying the system.

Example:
```python
result = await run_query_script(
    hostname="192.168.1.100",
    script="cat /var/log/syslog | grep ERROR",
    username="admin"  # Optional, defaults to root
)
```

### run_dangerous_script
Executes scripts that might modify the remote system. Includes safety confirmations and warnings.

Example:
```python
result = await run_dangerous_script(
    hostname="192.168.1.100",
    script="service nginx restart",
    username="admin",  # Optional, defaults to root
    confirmation="I understand this is dangerous"  # Required safety confirmation
)
```

## Installation

```bash
pip install ssh-mcp
```

## Usage

```bash
# Start the MCP server
ssh-mcp
```

## Requirements

- SSH key-based authentication must be set up for target machines
- Paramiko Python library (installed automatically)
- Python 3.12 or higher

## Configuration

Coming soon

## License

MIT 