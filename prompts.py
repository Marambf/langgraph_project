#prompts.py
"""
prompts.py - Contains all prompt templates and examples for the satellite imagery assistant
"""

from langchain.prompts import FewShotPromptTemplate, PromptTemplate

# System prompt (can be imported as 'system_prompt')
system_prompt = """
You are an intelligent assistant with access to various external tools to help answer user questions accurately. Please follow these essential rules:

1. Language: Always respond in the user's language (English or French).
2. Tool Use:
   - Use available tools only when needed to answer the question.
   - Never repeat the same tool call unless the user asked to.
3. Clarity & Structure:
   - Keep your responses clear, concise, and well-organized.
   - Do not continue reasoning once you have the necessary information.
4. Relevance:
   - Answer only the question asked. Do not assume extra intentions or add unrelated details.
5. Final Response Format:
   - Once you obtain an Observation, immediately return the response as:
    Final Answer: [your clear and concise reply]
6. Completeness:
   - Always include all relevant data obtained from tools (e.g., **all URLs**, values, statistics).
   - Never summarize or omit URLs. If multiple are returned, display them **explicitly and completely**.
   - Don’t omit tool outputs, even if the user didn’t explicitly request them.
7. Defaults:
   - If the user omits important details (e.g. date for weather), apply a sensible default (e.g., today’s date).

Available Tools (examples):
- get_date, get_time, calculator  
- get_external_data, get_weather_data, get_satellite_data  
- get_summary_stats, get_map_link


"""


# Example Q&A pairs
examples = [
  
    {
        "question": "Quelle est la date et l'heure actuelle ?",
        "response": (
            "Action: get_date()\nObservation: 01/07/2025\n"
            "Action: get_time()\nObservation: 14h30\n"
            "Final Answer: Nous sommes le 01/07/2025 et il est 14h30."
        )
    },
    {
        "question": "Calcule 23 * 17 et donne-moi la météo à Tunis",
        "response": (
            "Action: calculator('23*17')\nObservation: 391\n"
            "Action: weather('Tunis')\nObservation: Ensoleillé, 28°C\n"
            "Final Answer: Le résultat de 23 * 17 est 391. La météo à Tunis aujourd'hui (6 juillet 2025) : Ensoleillé, 28°C."
        )
    },
    {
        "question": "Images Sentinel-2 de Paris entre le 1er et 15 juin 2023",
        "response": (
            "Action: query_stac_catalog('Paris 2023-06-01 2023-06-15 sentinel-2-l2a')\nObservation: 5 images disponibles\n"
            "Final Answer: Voici les images Sentinel-2 : (https://example.com/S2A_20230605), (https://example.com/S2A_20230612), (https://example.com/S2A_20230620)"
        )
    },
    
    {
        "question": "Quel est l'indice de végétation autour de Lyon ?",
        "response": (
            "Action: get_sentinelhub_ndvi('Lyon')\nObservation: NDVI moyen = 0.82\n"
            "Final Answer: L'indice de végétation autour de Lyon est de 0.82 (élevé)"
        )
    },
    {
        "question": "Images Sentinel-2 entre 10.1,36.7,10.3,36.9 du 1er au 10 juillet 2025",
        "response": (
            "Action: get_satellite_images('10.1,36.7,10.3,36.9 2025-07-01 2025-07-10 sentinel-2-l2a')\n"
            "Observation: 3 images disponibles\n"
            "Final Answer: Voici les images Sentinel-2 pour la zone spécifiée : "
            "(https://example.com/S2A_20250702), "
            "(https://example.com/S2A_20250705), "
            "(https://example.com/S2A_20250709)"
        )
    },
    {
        "question": "What time is it?",
        "response": (
            "Action: get_time()\nObservation: 15h42\n"
            "Final Answer: The current time is 15h42."
        )
    }
,
    {
        "question": "What time is it?",
        "response": (
            "Action: get_time()\nObservation: 15h42\n"
            "Final Answer: The current time is 15h42."
        )
    }
,
    {
        "question": "Quelle est la date d'aujourd'hui ?",
        "response": (
            "Action: get_date()\nObservation: 10/07/2025\n"
            "Final Answer: Nous sommes le 10/07/2025."
    )
    },
        {
        "question": "Images Sentinel-1 de Marseille du 1er au 15 septembre 2023",
        "response": (
            "Action: get_satellite_images('Marseille 2023-09-01 2023-09-15 sentinel-1-grd')\n"
            "Observation: 4 images disponibles\n"
            "Final Answer: Voici les images Sentinel-1 : "
            "(https://example.com/S1A_20230903_GRD), "
            "(https://example.com/S1A_20230906_GRD), "
            "(https://example.com/S1A_20230909_GRD), "
            "(https://example.com/S1A_20230912_GRD)"
        )
    },
    
 
]

# Template for each example
example_template = PromptTemplate(
    input_variables=["question", "response"],
    template="""
Question: {question}
{response}
"""
)
# Main few-shot prompt template
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_template,
    prefix=system_prompt ,
    suffix="""
Question: {input}
Réponse (utilise le même format Action/Observation/Final Answer):
""",
    input_variables=["input"],
    example_separator="\n" + "-"*50 + "\n"
)

# Simple prompt for basic queries
simple_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
{system_prompt}

Question: {input}
Réponse concise:
"""
)

def get_prompt_config(mode="few_shot"):
    """Returns the requested prompt configuration"""
    return {
        "few_shot": few_shot_prompt,
        "simple": simple_prompt
    }.get(mode, few_shot_prompt)