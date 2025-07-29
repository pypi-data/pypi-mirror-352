from mcp_server_testing.server import mcp


def main():
    """MCP Test Server - A simple test server implementation"""
    import os
    import argparse

    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Run server with configurable transport and network settings")
    parser.add_argument('--sse', choices=['on', 'off'], default='off',
                        help='Enable SSE transport if set to "on"')
    parser.add_argument('--host',
                        default="localhost",
                        help='Host to bind the server to (default: localhost)')
    parser.add_argument('--port',
                        type=int,
                        default=8000,
                        help='Port to bind the server to (default: 8000)')
    parser.add_argument('--log-level',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info',
                        help='Set logging level:\n'
                             '  debug: Detailed debug information\n'
                             '  info: General execution information (default)\n'
                             '  warning: Potential issues that don\'t affect execution\n'
                             '  error: Errors that occur during execution')
    args = parser.parse_args()

    print("hoge")

    # Run server with configured settings
    if args.sse == 'on':
        mcp.run(
            transport="sse",
            host=args.host,
            port=args.port,
            log_level=args.log_level
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
