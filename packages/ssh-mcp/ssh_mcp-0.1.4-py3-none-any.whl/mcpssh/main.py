"""Main entry point for MCP SSH Server."""

import logging
import os
import sys
from typing import Dict, Any, Optional

import paramiko
from mcp.server.fastmcp import FastMCP

from .query_passman import query_passman

# Initialize FastMCP server
mcp = FastMCP("SSH server for remote machine access and management")

__version__ = "0.1.4"

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stderr)
logger = logging.getLogger("mcpssh")


@mcp.tool()
async def run_query_script(
        nick_name: str,
        script: str,
) -> Dict[str, Any]:
    """
    Run a read-only query script on a remote server via SSH.

    This tool is intended for safe, read-only operations that gather information
    without modifying the remote system. Examples include checking system status,
    viewing logs, listing files, etc.

    IMPORTANT FOR LLMs: This tool should ONLY be used for non-destructive, read-only
    operations. If your script might modify the system in any way, use run_dangerous_script
    instead. Common safe commands include: ls, cat, grep, ps, top, df, free, etc.

    Args:
        nick_name: The nickname of the remote server
        script: Shell script to run (must be read-only, e.g. 'ls -la', 'cat /proc/cpuinfo')

    Returns:
        Dictionary containing stdout, stderr, and exit status
    """
    # Load token from environment variable or configuration
    passman_token = os.environ.get("PASSMAN_TOKEN", "")
    jzon = query_passman("ssh", nick_name, passman_token)

    return await run_query_script_internal(
        hostname=jzon["host"],
        script=script,
        username=jzon["username"],
        port=jzon.get("port", 22),
    )


async def run_query_script_internal(
        hostname: str,
        script: str,
        username: Optional[str] = "root",
        port: int = 22,
) -> Dict[str, Any]:
    """
    Run a read-only query script on a remote server via SSH.

    This tool is intended for safe, read-only operations that gather information
    without modifying the remote system. Examples include checking system status,
    viewing logs, listing files, etc.

    IMPORTANT FOR LLMs: This tool should ONLY be used for non-destructive, read-only
    operations. If your script might modify the system in any way, use run_dangerous_script
    instead. Common safe commands include: ls, cat, grep, ps, top, df, free, etc.

    Args:
        hostname: Remote server hostname or IP address
        script: Shell script to run (must be read-only, e.g. 'ls -la', 'cat /proc/cpuinfo')
        username: SSH username (default: root)
        port: SSH port (default: 22)

    Returns:
        Dictionary containing stdout, stderr, and exit status
    """
    logger.info(f"Executing query script on {hostname}...")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using SSH key authentication
        client.connect(hostname, port=port, username=username)

        # Execute the script
        stdin, stdout, stderr = client.exec_command(script)
        exit_status = stdout.channel.recv_exit_status()

        # Get the output
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()

        client.close()

        return {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_status": exit_status,
            "success": exit_status == 0
        }

    except Exception as e:
        logger.error(f"SSH query error: {str(e)}")
        return {
            "error": str(e),
            "success": False
        }


@mcp.tool()
async def run_dangerous_script(
        nick_name: str,
        script: str,
        confirmation: str = "I understand this is dangerous",
) -> Dict[str, Any]:
    """
    Run a potentially dangerous script that may modify a remote system.

    ⚠️ CAUTION: This tool can make destructive changes to remote systems.
    Only use when you need to modify files, restart services, or make other changes.

    IMPORTANT FOR LLMs:
    1. Use this tool ONLY when the query explicitly requires changing something on the remote system
    2. Always explain the risks to the user before running dangerous commands
    3. Verify that your script is appropriate for the task and minimizes risks
    4. Consider using temporary files/backups when possible
    5. Common dangerous commands include: rm, mv, chmod, chown, service restart, etc.
    6. The 'confirmation' parameter must be provided exactly as "I understand this is dangerous"

    Args:
        nick_name: The nickname of the remote server
        script: Shell script to run that may modify the system
        confirmation: Safety confirmation string, must be "I understand this is dangerous"

    Returns:
        Dictionary containing stdout, stderr, and exit status
    """
    # Load token from environment variable or configuration
    passman_token = os.environ.get("PASSMAN_TOKEN", "")
    jzon = query_passman("ssh", nick_name, passman_token)

    return await run_dangerous_script_internal(
        hostname=jzon["hostname"],
        script=script,
        username=jzon["username"],
        port=jzon.get("port", 22),
        confirmation=confirmation,
    )


async def run_dangerous_script_internal(
        hostname: str,
        script: str,
        username: Optional[str] = "root",
        port: int = 22,
        confirmation: str = "I understand this is dangerous",
) -> Dict[str, Any]:
    """
    Run a potentially dangerous script that may modify a remote system.
    
    ⚠️ CAUTION: This tool can make destructive changes to remote systems.
    Only use when you need to modify files, restart services, or make other changes.
    
    IMPORTANT FOR LLMs:
    1. Use this tool ONLY when the query explicitly requires changing something on the remote system
    2. Always explain the risks to the user before running dangerous commands
    3. Verify that your script is appropriate for the task and minimizes risks
    4. Consider using temporary files/backups when possible
    5. Common dangerous commands include: rm, mv, chmod, chown, service restart, etc.
    6. The 'confirmation' parameter must be provided exactly as "I understand this is dangerous"
    
    Args:
        hostname: Remote server hostname or IP address
        script: Shell script to run that may modify the system
        username: SSH username (default: root)
        port: SSH port (default: 22)
        confirmation: Safety confirmation string, must be "I understand this is dangerous"
    
    Returns:
        Dictionary containing stdout, stderr, and exit status
    """
    if confirmation != "I understand this is dangerous":
        return {
            "error": "Safety confirmation string does not match. Must be exactly: 'I understand this is dangerous'",
            "success": False
        }

    logger.warning(f"Executing dangerous script on {hostname}! Content: {script}")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using SSH key authentication
        client.connect(hostname, port=port, username=username)

        # Execute the script
        stdin, stdout, stderr = client.exec_command(script)
        exit_status = stdout.channel.recv_exit_status()

        # Get the output
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()

        client.close()

        return {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_status": exit_status,
            "success": exit_status == 0,
            "warning": "This was a potentially dangerous operation. Verify the results carefully."
        }

    except Exception as e:
        logger.error(f"SSH dangerous script error: {str(e)}")
        return {
            "error": str(e),
            "success": False
        }


def main():
    """Run the MCP SSH server when called directly."""
    print(f"Starting SSH MCP Server for version {__version__}...")
    mcp.run()


if __name__ == "__main__":
    main()
