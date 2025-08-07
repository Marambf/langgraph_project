# nodes.py
from langchain.tools import tool
from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
from tools_risk import get_all_tools
from prompts import get_prompt_config


from tools_risk import extract_bbox_and_dates, query_stac_catalog_with_retry

@tool
def build_query_params_from_input(user_input: str) -> str:
    """
    Extrait bbox, dates, collection depuis une phrase libre et construit la chaîne 'params' attendue par STAC.
    """
    extraction_result = extract_bbox_and_dates({"user_input": user_input})
    
    if "error" in extraction_result:
        return extraction_result["error"]

    bbox = extraction_result["bbox"]
    start_date = extraction_result["start_date"]
    end_date = extraction_result["end_date"]
    collection = extraction_result["collection"]

    return f"{bbox} {start_date} {end_date} {collection}"



def create_agent_executor():
    # Récupérer le prompt formaté
    prompt_template = get_prompt_config("few_shot")
    system_prompt_str = prompt_template.format(input="Votre question ici")

    llm = OllamaLLM(
        model="mistral",
        temperature=0.1,
        system_prompt=system_prompt_str,
    )

    tools = get_all_tools()

    agent_executor = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        max_iterations=6  
    )

    return agent_executor

from tools_risk import extract_bbox_and_dates, query_stac_catalog_with_retry

def run_query_direct(user_input: str):
    result = extract_bbox_and_dates(user_input)
    if "error" in result:
        return result["error"]

    bbox = result["bbox"]
    start = result["start_date"]
    end = result["end_date"]
    collection = result["collection"]

    params = f"{bbox} {start} {end} {collection}"
    return query_stac_catalog_with_retry(params)