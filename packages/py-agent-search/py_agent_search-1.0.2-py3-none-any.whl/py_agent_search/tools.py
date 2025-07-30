from langchain_community.tools import WikipediaQueryRun, YouTubeSearchTool, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from .stream import StreamingCallbackHandler

handler = StreamingCallbackHandler()

# 1. Istanziamo DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun(
    verbose=True,
    name="duckduckgo_search",
    description="Use this tool to search for information on the internet via DuckDuckGo.",
    callbacks=[handler],
    return_direct=False,
    response_format="content"
)

api_wrapper = WikipediaAPIWrapper(wiki_client=None, top_k_results=1, doc_content_chars_max=100)
wikipedia_tool = WikipediaQueryRun(
    api_wrapper=api_wrapper, 
    name="wikipedia_search",
    description="Use this tool to search for information on Wikipedia.",
    verbose=True, 
    callbacks=[handler], 
    return_direct=False,
    response_format="content"
)

youtube_tool = YouTubeSearchTool(
    name="youtube_search",
    description="Use this tool to search for videos on YouTube.",
    verbose=True,
    callbacks=[handler],
    return_direct=False,
    response_format="content"
)