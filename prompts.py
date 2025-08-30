
#prompts.py
"""
prompts.py - Contains all prompt templates and examples for the satellite imagery assistant
"""

from langchain.prompts import FewShotPromptTemplate, PromptTemplate

# System prompt (can be imported as 'system_prompt')
system_prompt = """
You are an intelligent assistant with access to various external tools to help answer user questions accurately. Please follow these essential rules:

1. Language: Always respond in the language used by the user, whether it is English, French, or any other language. Ensure your understanding and response match the language of the input.2. Tool Use:
   - Use available tools only when needed to answer the question.
   - Never repeat the same tool call unless the user asked to.
   - If a tool call is made, always provide the output in the final answer.
   -You will receive questions in any language. Always internally translate the input question to English before reasoning.  
        After you generate your answer in English, translate the final answer back to the original input language.  
        Respond to the user in their original language.



2. Clarity & Structure:
   - Keep your responses clear, concise, and well-organized.
   - Do not continue reasoning once you have the necessary information.
3. Relevance:
   - Answer only the question asked. Do not assume extra intentions or add unrelated details.
4. Final Response Format:
   - Once you obtain an Observation, immediately return the response as:
    Final Answer: [your clear and concise reply]
5. Completeness:
   - Always include all relevant data obtained from tools (e.g., **all URLs**, values, statistics).
   - Never summarize or omit URLs. If multiple are returned, display them **explicitly and completely**.
   - Don’t omit tool outputs, even if the user didn’t explicitly request them.
6. Defaults:
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
            "Action: get_date()\n"
            "Observation: 01/07/2025\n"
            "Action: get_time()\n"
            "Observation: 14h30\n"
            "Final Answer: Nous sommes le 01/07/2025 et il est 14h30."
        )
    },
    {
        "question": "Calcule 23 * 17 et donne-moi la météo à Tunis",
        "response": (
            "Action: calculator('23*17')\n"
            "Observation: 391\n"
            "Action: weather('Tunis')\n"
            "Observation: Ensoleillé, 28°C\n"
            "Final Answer: Le résultat de 23 * 17 est 391. La météo à Tunis aujourd'hui (6 juillet 2025) : Ensoleillé, 28°C."
        )
    },
    {
        "question": "Images Sentinel-2 de Paris entre le 1er et 15 juin 2023",
        "response": (
            "Action: get_satellite_images('Paris 2023-06-01 2023-06-15 sentinel-2-l2a')\nObservation: 5 images disponibles\n"
            "Final Answer: Voici les images Sentinel-2 : (https://example.com/S2A_20230605), (https://example.com/S2A_20230612), (https://example.com/S2A_20230620)"
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
        "question": "what time is ?",
        "response": (
            "Action: get_time()\n"
            "Observation: 15h42\n"
            "Final Answer: it is 15h42."
        )
    },
    {
        "question": "Quelle est la date d'aujourd'hui ?",
        "response": (
            "Action: get_date()\n"
            "Observation: 10/07/2025\n"
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
    {
    "question": "Y a-t-il eu des incendies près de Gafsa entre le 1er et le 10 août 2023 ?",
    "response": (
        "Action: detect_fire_tool(city_name='Gafsa', target_date='2023-08-01 to 2023-08-10')\n"
        "Observation: 12 foyers d'incendies détectés entre le 1er et le 10 août 2023 près de Gafsa.\n"
        "Final Answer: 12 incendies ont été détectés autour de Gafsa entre le 1er et le 10 août 2023."
    )
}
,
    {
    "question": "Were there any fires near Algiers in July 2022?",
    "response": (
        "Action: detect_fire_tool(city_name='Algiers', target_date='2022-07-01 to 2022-07-31')\n"
        "Observation: 8 fire events recorded near Algiers during July 2022.\n"
        "Final Answer: Yes, 8 fires were recorded near Algiers in July 2022."
    )
},

    {
    "question": "Incendies récents autour de Bizerte ?",
    "response": (
        "Action: get_date()\n"
        "Observation: 2025-07-21\n"
        "Action: detect_fire_tool(city_name='Bizerte', target_date='2025-07-21')\n"
        "Observation: 3 foyers actifs détectés le 21 juillet 2025 autour de Bizerte.\n"
        "Final Answer: 3 incendies sont actuellement actifs autour de Bizerte (détectés le 21 juillet 2025)."
    )
},
{
    "question": "Montre-moi les inondations en France le 3 juin 2023",
    "response": (
        "Action: query_disaster_events_tool(country_name='France', date_expression='3 juin 2023', disaster_type='flood')\n"
        "Observation: Inondations détectées en France entre 2023-06-03 et 2023-06-03 :\n"
        "- Flood in Paris (2023-06-03 ➝ 2023-06-03)\n"
        "Final Answer: Une inondation a été détectée à Paris le 3 juin 2023."
    )
},
{
    "question": "Show me the floods in Italy on May 10, 2022",
    "response": (
        "Action: query_disaster_events_tool(country_name='Italy', date_expression='May 10, 2022', disaster_type='flood')\n"
        "Observation: Floods detected in Italy between 2022-05-10 and 2022-05-10:\n"
        "- Flood in Venice (2022-05-10 ➝ 2022-05-10)\n"
        "Final Answer: A flood was detected in Venice on May 10, 2022."
    )
},
{
    "question": "Quelles sont les inondations survenues en Allemagne entre janvier et mars 2023 ?",
    "response": (
        "Action: query_disaster_events_tool(country_name='Allemagne', date_expression='entre janvier et mars 2023', disaster_type='flood')\n"
        "Observation: Inondations détectées en Allemagne entre 2023-01-01 et 2023-03-31 :\n"
        "- Flood in Berlin (2023-01-15 ➝ 2023-01-17)\n"
        "- Flood in Hamburg (2023-03-02 ➝ 2023-03-03)\n"
        "Final Answer: Deux inondations ont été détectées en Allemagne entre janvier et mars 2023 : à Berlin et à Hambourg."
    )
},
{
    "question": "Were there any storms in the Philippines in July 2021?",
    "response": (
        "Action: query_disaster_events_tool(country_name='Philippines', date_expression='July 2021', disaster_type='storm')\n"
        "Observation: Storms detected in Philippines between 2021-07-01 and 2021-07-31:\n"
        "- Storm in Luzon (2021-07-08 ➝ 2021-07-10)\n"
        "Final Answer: A storm was detected in Luzon in July 2021."
    )
},
{
    "question": "Were there any earthquakes in Peru in March 2022?",
    "response": (
        "Action: query_disaster_events_tool(country_name='Peru', date_expression='March 2022', disaster_type='earthquake')\n"
        "Observation: Earthquakes detected in Peru between 2022-03-01 and 2022-03-31:\n"
        "- Earthquake in Lima (2022-03-14 ➝ 2022-03-16)\n"
        "Final Answer: An earthquake was detected in Lima in March 2022."
    )
},
    
{
        "question": "Évalue le risque d’infiltration d’eau de surface à Paris",
        "response": (
            "Action: estimate_surface_water_ingress_tool(location_input='Paris')\n"
            "Observation: \n"
            "  Ingress_paths_estimate: L’eau suit les lignes d’écoulement (D8) vers les points bas.\n"
            "  Mitigation_actions: Créer des rigoles ou bermes, Installer un drain français, Nettoyer les grilles, Vérifier étanchéité\n"
            "  Statistics: DEM_shape=(200,200), Elevation_min=28.5, Elevation_max=112.3, Elevation_mean=57.2, Slope_mean=0.018, Risk_zone_percent=12.7\n"
            "  Maps: Elevation=map_elevation.png, Slope=map_slope.png, FlowAccumulation=map_flowacc.png, Risk=map_risk.png, Risk_Folium=map_risk_folium.html\n"
            "  Explanation: 📊 Comment lire les cartes ...\n"
            "Final Answer: Voici l’évaluation du risque d’infiltration d’eau de surface à Paris, avec statistiques, actions de mitigation et cartes générées."
        )
    },
    {
        "question": "Estimate surface water ingress risk for New York City",
        "response": (
            "Action: estimate_surface_water_ingress_tool(location_input='New York City')\n"
            "Observation: \n"
            "  Ingress_paths_estimate: Water follows D8 flow lines towards low points.\n"
            "  Mitigation_actions: Create channels or berms to divert water upstream, Install French drains along flow lines, Regularly clean grates and inlets, Check waterproofing of thresholds and joints\n"
            "  Statistics: DEM_shape=(210,210), Elevation_min=2.5, Elevation_max=41.3, Elevation_mean=14.7, Slope_mean=0.022, Risk_zone_percent=18.4\n"
            "  Maps: Elevation=map_elevation.png, Slope=map_slope.png, FlowAccumulation=map_flowacc.png, Risk=map_risk.png, Risk_Folium=map_risk_folium.html\n"
            "  Explanation: 📊 How to read the maps: 1. Elevation map: darker = lower areas. 2. Slope map: steeper slopes = faster runoff. 3. Flow accumulation: likely water paths. 4. Risk map: red zones = potential water accumulation.\n"
            "Final Answer: Here is the surface water ingress risk assessment for New York City, including statistics, mitigation actions, and generated maps."
        )
    },
    {
        "question": "Can you provide a detailed surface water risk analysis for New York City?",
        "response": (
            "Action: estimate_surface_water_ingress_tool(location_input='New York City')\n"
            "Observation: \n"
            "  Ingress_paths_estimate: Water follows D8 flow lines towards low points.\n"
            "  Mitigation_actions: Create channels or berms to divert water upstream, Install French drains along flow lines, Regularly clean grates and inlets, Check waterproofing of thresholds and joints\n"
            "  Statistics: DEM_shape=(210,210), Elevation_min=2.5, Elevation_max=41.3, Elevation_mean=14.7, Slope_mean=0.022, Risk_zone_percent=18.4\n"
            "  Maps: Elevation=map_elevation.png, Slope=map_slope.png, FlowAccumulation=map_flowacc.png, Risk=map_risk.png, Risk_Folium=map_risk_folium.html\n"
            "  Explanation: 📊 How to read the maps: 1. Elevation map: darker = lower areas. 2. Slope map: steeper slopes = faster runoff. 3. Flow accumulation: likely water paths. 4. Risk map: red zones = potential water accumulation.\n"
            "Final Answer: Here is the surface water ingress risk assessment for New York City, including statistics, mitigation actions, and generated maps."
        )
    }

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