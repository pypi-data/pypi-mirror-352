"""
Command-line interface for VSCode Command Client
"""

import argparse
import json
import sys
import time
from typing import List, Optional

from .client import VSCodeHTTPClient


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="VSCode Command Client - Execute VSCode commands remotely",
        epilog="Examples:\n"
               "  vscode-client status\n"
               "  vscode-client execute workbench.action.showCommands\n"
               "  vscode-client commands --limit 10\n"
               "  vscode-client info\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=3000,
        help="Server port (default: 3000)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Check server status")
    
    # Info command
    subparsers.add_parser("info", help="Get server information")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a VSCode command")
    execute_parser.add_argument("vscode_command", help="VSCode command to execute")
    execute_parser.add_argument("args", nargs="*", help="Command arguments (JSON format)")
    
    # Commands list
    commands_parser = subparsers.add_parser("commands", help="List available commands")
    commands_parser.add_argument("--limit", "-l", type=int, help="Limit number of commands shown")
    commands_parser.add_argument("--filter", "-f", help="Filter commands by substring")
    
    # Wait command
    wait_parser = subparsers.add_parser("wait", help="Wait for server to become available")
    wait_parser.add_argument("--max-wait", type=int, default=30, help="Maximum wait time in seconds")
    
    return parser


def format_output(data: dict, json_format: bool = False) -> str:
    """Format output data."""
    if json_format:
        return json.dumps(data, indent=2)
    
    if not data.get("success", False):
        return f"❌ Error: {data.get('error', 'Unknown error')}"
    
    return f"✅ Success: {data.get('message', 'Operation completed')}"


def handle_status(client: VSCodeHTTPClient, args) -> int:
    """Handle status command."""
    result = client.check_status()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✅ Server is running on {client.base_url}")
            if "message" in result:
                print(f"📋 Status: {result['message']}")
        else:
            print(f"❌ Server is not running: {result.get('error')}")
            return 1
    
    return 0


def handle_info(client: VSCodeHTTPClient, args) -> int:
    """Handle info command."""
    result = client.get_server_info()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"📊 Server Information:")
            print(f"   URL: {client.base_url}")
            print(f"   Port: {result.get('port')}")
            print(f"   PID: {result.get('pid')}")
            print(f"   Workspace: {result.get('workspace', 'Not specified')}")
        else:
            print(f"❌ Error: {result.get('error')}")
            return 1
    
    return 0


def handle_execute(client: VSCodeHTTPClient, args) -> int:
    """Handle execute command."""
    # Parse arguments as JSON if provided
    parsed_args = []
    for arg in args.args:
        try:
            parsed_args.append(json.loads(arg))
        except json.JSONDecodeError:
            parsed_args.append(arg)
    
    result = client.execute_command(args.vscode_command, parsed_args if parsed_args else None)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✅ Command executed: {args.vscode_command}")
            if result.get("result"):
                print(f"📋 Result: {result['result']}")
        else:
            print(f"❌ Command failed: {result.get('error')}")
            return 1
    
    return 0


def handle_commands(client: VSCodeHTTPClient, args) -> int:
    """Handle commands list command."""
    result = client.get_commands()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            commands = result.get("commands", [])
            
            # Apply filter if specified
            if args.filter:
                commands = [cmd for cmd in commands if args.filter.lower() in cmd.lower()]
            
            # Apply limit if specified
            if args.limit:
                commands = commands[:args.limit]
            
            print(f"📝 Found {len(commands)} commands:")
            for i, cmd in enumerate(commands, 1):
                print(f"   {i}. {cmd}")
                
            if args.limit and len(result.get("commands", [])) > args.limit:
                remaining = len(result.get("commands", [])) - args.limit
                print(f"   ... and {remaining} more commands")
        else:
            print(f"❌ Error: {result.get('error')}")
            return 1
    
    return 0


def handle_wait(client: VSCodeHTTPClient, args) -> int:
    """Handle wait command."""
    print(f"⏳ Waiting for server at {client.base_url}...")
    
    if client.wait_for_server(args.max_wait):
        print("✅ Server is now available!")
        return 0
    else:
        print(f"❌ Timeout: Server did not become available within {args.max_wait} seconds")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    client = VSCodeHTTPClient(
        port=args.port,
        host=args.host,
        timeout=args.timeout
    )
    
    try:
        if args.command == "status":
            return handle_status(client, args)
        elif args.command == "info":
            return handle_info(client, args)
        elif args.command == "execute":
            return handle_execute(client, args)
        elif args.command == "commands":
            return handle_commands(client, args)
        elif args.command == "wait":
            return handle_wait(client, args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main()) 