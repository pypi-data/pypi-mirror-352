import contextlib
import logging
from collections.abc import AsyncIterator

# - click: 帮你写命令行参数，比如 --api-key=xxx。
import click

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

# - starlette: 帮你搭建 HTTP 网络服务。
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

import json
import base64

async def file_to_base64(file_path: str) -> str:
    """
    将存储在本地电脑的文件转换为Base64编码
    :param file_path: 文件的绝对路径
    :return: Base64编码的字符串
    """
    try:
        with open(file_path, "rb") as general_file:
            file_data = general_file.read()
            base64_encoded_data = base64.b64encode(file_data)
            base64_message = base64_encoded_data.decode('utf-8')
            return base64_message
    except Exception as e:
        print(f"发生错误: {e}")
        return None


@click.command()
@click.option("--port", default=8000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(port: int, log_level: str, json_response: bool) -> int:
    # ---------------------- Configure logging ----------------------
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("rpa_idp_server")

    # ---------------------- Create MCP Server ----------------------
    app = Server("rpa_idp_server")

    # ---------------------- Tool implementation -------------------
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls."""
        ctx = app.request_context

        # Initialize a list to hold the results from each tool execution
        results = []

        try:
            if name == "file_to_base64":
                file_path = arguments.get("local_file_path")
                if not file_path:
                    raise ValueError("'local_file_path' is required in arguments")
                await ctx.session.send_log_message(
                    level="info",
                    data=f"dealing with {file_path}",
                    logger="resume",
                    related_request_id=ctx.request_id,
                )

                # 发送消息给客户端，告知开始处理
                await ctx.session.send_log_message(
                    level="info",
                    data="准备开始转换文件"+file_path,
                    logger="resume",
                    related_request_id=ctx.request_id,
                )

                base_64_content = await file_to_base64(file_path)
                # Convert the result to a JSON string for display
                # base_64_content_json = json.dumps(base_64_content, ensure_ascii=False)
                results.append(types.TextContent(type="text", text=base_64_content))

            else:
                # Handle unknown tools or add default behavior
                await ctx.session.send_log_message(
                    level="error",
                    data=f"Unknown tool '{name}' requested.",
                    logger="error",
                    related_request_id=ctx.request_id,
                )
                raise ValueError(f"Unknown tool '{name}' requested.")

        except Exception as err:
            await ctx.session.send_log_message(
                level="error",
                data=str(err),
                logger="error",
                related_request_id=ctx.request_id,
            )
            raise  # Re-raise to let MCP know an error occurred

        return results

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Expose available tools to the LLM."""
        return [
            types.Tool(
                name="file_to_base64",
                description="读取一个本机的文件，将内容转化为base64编码",
                inputSchema={
                    "type": "object",
                    "required": ["local_file_path"],
                    "properties": {
                        "local_file_path": {
                            "type": "string",
                            "description": "本地文件的绝对路径"
                        }
                    }
                },
                annotations={
                }
            )
        ]

    # ---------------------- Session manager -----------------------
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # 无状态；不保存历史事件
        json_response=json_response, # 采用流式SSE
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D401,E501
        await session_manager.handle_request(scope, receive, send)

    # ---------------------- Lifespan Management --------------------
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            logger.info("rpa_idp MCP server started! 🚀")
            try:
                yield
            finally:
                logger.info("rpa_idp MCP server shutting down…")

    # ---------------------- ASGI app + Uvicorn ---------------------
    starlette_app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_streamable_http)],
        lifespan=lifespan,
    )

    import uvicorn

    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0


if __name__ == "__main__":
    main()