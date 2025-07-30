from mcp.server import FastMCP

app = FastMCP('hello-world')


@app.tool()
async def hello(name: str) -> str:
    """给对方欢迎提示语

    Args:
        name (str): 任何人的名字，当然，不是名字也行

    Returns:
        str: 欢迎提示语
    """
    return f"hello,{name}!"

if __name__ == '__main__':
    app.run(transport='stdio')
