from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os
import json
from bs4 import BeautifulSoup
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
def get_docs(query:str):
    
    


def main():
    print("Hello from mcp-server!")


if __name__ == "__main__":
    main()
