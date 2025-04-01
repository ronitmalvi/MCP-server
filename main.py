from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os
import json
from bs4 import BeautifulSoup # type: ignore
load_dotenv()

mcp=FastMCP("docs")

USER_AGENT="docs-app/1.0"
SERPER_URL="https://google.serper.dev/search"

docs_url={
    "langchain":"python.langchain.com/docs",
    "llama-index":"docs.llamaindex.ai/en/stable",
    "openai":"platform.openai.com/docs",
}

async def search_web(query: str)->dict | None:
    payload=json.dumps({"q":query,"num":2})

    headers={
        "X-API-KEY":os.getenv("SERPER_API_KEY"),
        "Content-Type":"application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response=await client.post(SERPER_URL,data=payload,headers=headers,timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"organic":[]}
    


async def fetch_url(url:str):
    async with httpx.AsyncClient() as client:
        try:
            response=await client.get(url,timeout=30)
            soup=BeautifulSoup(response.text,"html.parser")
            text=soup.get_text()
            return text
        except httpx.TimeoutException:
            return "Timeout Error"

@mcp.tool()
async def get_docs(query:str,library:str):
    """
    Search the docs for a given query and Library.
    Supports langchain, openai, and llama-index.

    Args :
    query: The query to search for (e.g. "Chroma DB")
    library: The library to search in (e.g. "langchain")

    Returns:
    Text from documentation
    """
    if library not in docs_url:
        raise ValueError(f"Library {library} not supported by this tool")
    
    query=f"site:{docs_url[library]} {query}"
    results= await search_web(query)

    if len(results["organic"])==0:
        return "No results found"
    
    text=""
    for result in results["organic"]:
        text+=await fetch_url(result["link"])
    return text


if __name__ == "__main__":
    mcp.run(transport="stdio")