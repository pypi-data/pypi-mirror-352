from .server import serve


def main():
    """MCP Check Server - Check CVE functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to make web requests"
    )
    parser.add_argument("--apikey", type=str, default="SPK1HgBWcxO5EmLsCSP6aIRNhX6wXMYa", help="API key to use for requests")

    args = parser.parse_args()
    asyncio.run(serve(args.apikey))


if __name__ == "__main__":
    main()
