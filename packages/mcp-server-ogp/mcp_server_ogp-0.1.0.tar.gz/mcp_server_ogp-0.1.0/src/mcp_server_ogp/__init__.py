from mcp_server_ogp.server import mcp


def main():
    """
    OGP Information Server - Model Context Protocol server for extracting Open Graph Protocol information
    
    This server extracts OGP (Open Graph Protocol) information from specified URLs,
    providing metadata commonly used for social media sharing previews.
    
    Available features:
    1. ogp-info: Extract OGP information from URLs
    2. ogp-image: Fetch OGP images and return as Base64-encoded data
    """
    import os
    import argparse

    # Command line argument configuration
    # This allows customization of server behavior
    parser = argparse.ArgumentParser(
        description="Start the OGP information extraction server. Extract Open Graph Protocol metadata from web pages.")
    parser.add_argument('--sse', choices=['on', 'off'], default='off',
                        help='Enable SSE transport when set to "on"')
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
                             '  warning: Potential issues that do not affect execution\n'
                             '  error: Errors that occur during execution')
    args = parser.parse_args()

    print("Starting OGP Information Server...")
    print(f"Available tools: ogp-info, ogp-image")

    # Run server with configured arguments
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
