# agent/agent_executor.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import Tool

from tools.stac_query import query_stac_catalog
from tools.downloader import download_asset
from tools.metadata import extract_metadata
from tools.analysis_ndvi import calculate_ndvi
from tools.analysis_ndwi import calculate_ndwi
from tools.sar_analysis import analyze_sar
from tools.geocode import geocode_place

llm = ChatOllama(model="mistral")

tools = [
    Tool.from_function(query_stac_catalog),
    Tool.from_function(download_asset),
    Tool.from_function(extract_metadata),
    Tool.from_function(calculate_ndvi),
    Tool.from_function(calculate_ndwi),
    Tool.from_function(analyze_sar),
    Tool.from_function(geocode_place),
]

agent = create_react_agent(llm, tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)