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
    },
    {
    "question": "Montre-moi les risques naturels à Paris",
    "response": (
        "Action: think_hazard('Paris')\n"
        "Observation: Top 5 hazards for this location (Paris, Île-de-France, France):\n"
        "- River flood: High\n"
        "- Wildfire: Medium\n"
        "- Urban flood: Medium\n"
        "- Water scarcity: Low\n"
        "- Extreme heat: Medium\n"
        "--------------------------------------------------\n"
        "Final Answer: Voici les principaux risques naturels à Paris avec leurs niveaux de gravité."
    )
},
{
    "question": "Show me the top hazards in New York City",
    "response": (
        "Action: think_hazard('New York City')\n"
        "Observation: Top 5 hazards for this location (New York, NY, USA):\n"
        "- Urban flood: High\n"
        "- Extreme heat: Medium\n"
        "- River flood: Medium\n"
        "- Wildfire: Low\n"
        "- Water scarcity: Low\n"
        "--------------------------------------------------\n"
        "Final Answer: Here are the top natural hazards in New York City with their severity levels."
    )
},
{
    "question": "Évalue les dangers naturels pour les coordonnées 48.8566, 2.3522",
    "response": (
        "Action: think_hazard('48.8566, 2.3522')\n"
        "Observation: Top 5 hazards for this location (Paris, Île-de-France, France):\n"
        "- River flood: High\n"
        "- Urban flood: Medium\n"
        "- Extreme heat: Medium\n"
        "- Wildfire: Low\n"
        "- Water scarcity: Low\n"
        "--------------------------------------------------\n"
        "Final Answer: Voici les principaux risques naturels pour la localisation donnée avec leurs niveaux."
    )
},
{
    "question": "Give me the hazard assessment for Tokyo",
    "response": (
        "Action: think_hazard('Tokyo')\n"
        "Observation: Top 5 hazards for this location (Tokyo, Japan):\n"
        "- Earthquake: High\n"
        "- Urban flood: Medium\n"
        "- Extreme heat: Medium\n"
        "- River flood: Low\n"
        "- Wildfire: Low\n"
        "--------------------------------------------------\n"
        "Final Answer: Here are the main natural hazards in Tokyo with their risk levels."
    )
},
{
    "question": "Y a-t-il eu des températures extrêmes à Paris en juillet 2023 ?",
    "response": (
        "Action: query_disaster_events_tool(country_name='France', date_expression='juillet 2023', disaster_type='extreme temperature')\n"
        "Observation: Températures extrêmes détectées en France entre 2023-07-01 et 2023-07-31 :\n"
        "- Extreme temperature in Paris (2023-07-12 ➝ 2023-07-14)\n"
        "Final Answer: Des températures extrêmes ont été enregistrées à Paris entre le 12 et le 14 juillet 2023."
    )
},
{
    "question": "Were there any droughts in Spain in summer 2022?",
    "response": (
        "Action: query_disaster_events_tool(country_name='Spain', date_expression='summer 2022', disaster_type='drought')\n"
        "Observation: Droughts detected in Spain between 2022-06-01 and 2022-08-31:\n"
        "- Drought in Valencia (2022-06-15 ➝ 2022-08-20)\n"
        "Final Answer: A drought was recorded in Valencia during summer 2022."
    )
},
{
    "question": "Accidents industriels récents autour de Lyon ?",
    "response": (
        "Action: query_disaster_events_tool(country_name='France', date_expression='2025-07-15', disaster_type='industrial accident')\n"
        "Observation: 2 accidents industriels détectés autour de Lyon le 15 juillet 2025.\n"
        "Final Answer: Deux accidents industriels ont été détectés autour de Lyon le 15 juillet 2025."
    )
},
{
    "question": "Were there any transport accidents in New York City in March 2024?",
    "response": (
        "Action: query_disaster_events_tool(country_name='USA', date_expression='March 2024', disaster_type='transport')\n"
        "Observation: Transport accidents detected in New York City between 2024-03-01 and 2024-03-31:\n"
        "- Transport accident in Manhattan (2024-03-10)\n"
        "- Transport accident in Brooklyn (2024-03-22)\n"
        "Final Answer: Two transport accidents occurred in New York City in March 2024: one in Manhattan on March 10 and one in Brooklyn on March 22."
    )
},
{
    "question": "Donne-moi des informations sur la France",
    "response": (
        "Action: geo_info_tool(name='France')\n"
        "Observation: Type : Pays\nNom : France\nCapital : Paris\nPopulation : 67391582\nSuperficie (km²) : 551695\nRégion : Europe\nSous-région : Western Europe\nLangues : ['French']\nMonnaie : Euro\nDrapeau : https://flagcdn.com/w320/fr.png\n"
        "Final Answer: La France est un pays d'Europe dont la capitale est Paris. Elle compte environ 67 millions d'habitants et une superficie de 551 695 km²."
    )
},
{
    "question": "What can you tell me about Japan?",
    "response": (
        "Action: geo_info_tool(name='Japan')\n"
        "Observation: Type : Pays\nNom : Japan\nCapital : Tokyo\nPopulation : 125836021\nSuperficie (km²) : 377930\nRégion : Asia\nSous-région : Eastern Asia\nLangues : ['Japanese']\nMonnaie : Yen\nDrapeau : https://flagcdn.com/w320/jp.png\n"
        "Final Answer: Japan is an Asian country located in Eastern Asia. Its capital is Tokyo and it has a population of about 125 million."
    )
},
{
    "question": "Informations sur Casablanca",
    "response": (
        "Action: geo_info_tool(name='Casablanca')\n"
        "Observation: Type : Ville\nNom : Casablanca, Préfecture de Casablanca, Maroc\nPays : Morocco\nRégion : Casablanca-Settat\nLatitude : 33.58831\nLongitude : -7.61138\nPopulation : 3359818\n"
        "Final Answer: Casablanca est une ville marocaine située dans la région de Casablanca-Settat. Elle compte environ 3,3 millions d'habitants."
    )
},
{
    "question": "Tell me about New York",
    "response": (
        "Action: geo_info_tool(name='New York')\n"
        "Observation: Type : Ville\nNom : New York, New York County, New York, United States\nPays : United States\nRégion : New York\nLatitude : 40.7127281\nLongitude : -74.0060152\nPopulation : 8804190\n"
        "Final Answer: New York is a city in the United States, located in the state of New York. It has a population of about 8.8 million people."
    )
},
{
    "question": "Peux-tu me donner des infos sur l'Allemagne ?",
    "response": (
        "Action: geo_info_tool(name='Allemagne')\n"
        "Observation: Type : Pays\nNom : Germany\nCapital : Berlin\nPopulation : 83166711\nSuperficie (km²) : 357114\nRégion : Europe\nSous-région : Western Europe\nLangues : ['German']\nMonnaie : Euro\nDrapeau : https://flagcdn.com/w320/de.png\n"
        "Final Answer: L'Allemagne est un pays d'Europe centrale dont la capitale est Berlin. Sa population est d'environ 83 millions d'habitants."
    )
},
{
    "question": "Peux-tu me calculer la route entre Casablanca et Rabat ?",
    "response": (
        "Action: route_tool(start='Casablanca', end='Rabat')\n"
        "Observation: Distance totale : 87.4 km\nDurée estimée : 1 h 05 min\nÉtapes :\n"
        " 1. Départ sur Casablanca.\n"
        " 2. Prenez la bretelle à droite sur A1 (12 km).\n"
        " 3. Continuez tout droit sur A1 (75 km).\n"
        "Final Answer: L’itinéraire de Casablanca à Rabat dure environ 1 h 05 min pour 87 km. Une carte a été générée (`itineraire.html`)."
    )
},
{
    "question": "How do I go from New York to Boston?",
    "response": (
        "Action: route_tool(start='New York', end='Boston')\n"
        "Observation: Distance: 346.5 km\nEstimated duration: 3 h 45 min\nSteps:\n"
        " 1. Start in New York.\n"
        " 2. Take the ramp right onto I-95 North (15 km).\n"
        " 3. Continue on I-95 for 320 km.\n"
        "Final Answer: The trip from New York to Boston is about 346 km and takes around 3 h 45 min. The map has been saved in `itineraire.html`."
    )
},
{
    "question": "Itinéraire de Marseille à Nice",
    "response": (
        "Action: route_tool(start='Marseille', end='Nice')\n"
        "Observation: Distance totale : 200.7 km\nDurée estimée : 2 h 20 min\nÉtapes :\n"
        " 1. Départ sur Marseille.\n"
        " 2. Prenez la sortie vers A50.\n"
        " 3. Continuez sur A8 direction Nice.\n"
        "Final Answer: Le trajet Marseille → Nice fait environ 200 km et prend 2 h 20 min. Une carte interactive est disponible (`itineraire.html`)."
    )
},
{
    "question": "Peux-tu me donner la météo actuelle et les prévisions pour Paris ?",
    "response": (
        "Action: weather_tool(city_name='Paris')\n"
        "Observation: Météo actuelle à Paris : 18°C, vent 12 km/h.\n"
        "Prévisions :\n"
        "2025-08-31 : Max 22°C / Min 16°C / Pluie 0 mm\n"
        "2025-09-01 : Max 24°C / Min 17°C / Pluie 1 mm\n"
        "2025-09-02 : Max 21°C / Min 15°C / Pluie 0 mm\n"
        "Final Answer: À Paris, la température actuelle est de 18°C avec un vent de 12 km/h. Les prochains jours verront des températures comprises entre 15 et 24°C avec peu de pluie."
    )
},
{
    "question": "What is the weather like in Tokyo?",
    "response": (
        "Action: weather_tool(city_name='Tokyo')\n"
        "Observation: Current weather in Tokyo: 27°C, wind 8 km/h.\n"
        "Forecast:\n"
        "2025-08-31 : Max 30°C / Min 24°C / Rain 0 mm\n"
        "2025-09-01 : Max 31°C / Min 25°C / Rain 2 mm\n"
        "2025-09-02 : Max 29°C / Min 23°C / Rain 0 mm\n"
        "Final Answer: In Tokyo, the current temperature is 27°C with wind at 8 km/h. The next few days will range from 23 to 31°C with occasional rain."
    )
},
{
    "question": "Donne-moi la météo à Casablanca",
    "response": (
        "Action: weather_tool(city_name='Casablanca')\n"
        "Observation: Météo actuelle à Casablanca : 26°C, vent 15 km/h.\n"
        "Prévisions :\n"
        "2025-08-31 : Max 29°C / Min 21°C / Pluie 0 mm\n"
        "2025-09-01 : Max 30°C / Min 22°C / Pluie 0 mm\n"
        "2025-09-02 : Max 28°C / Min 21°C / Pluie 0 mm\n"
        "Final Answer: À Casablanca, il fait actuellement 26°C avec un vent de 15 km/h. Les températures prévues oscillent entre 21 et 30°C avec pas de pluie."
    )
},
{
    "question": "What's the weather forecast for New York?",
    "response": (
        "Action: weather_tool(city_name='New York')\n"
        "Observation: Current weather in New York: 23°C, wind 10 km/h.\n"
        "Forecast:\n"
        "2025-08-31 : Max 26°C / Min 20°C / Rain 1 mm\n"
        "2025-09-01 : Max 25°C / Min 19°C / Rain 0 mm\n"
        "2025-09-02 : Max 24°C / Min 18°C / Rain 2 mm\n"
        "Final Answer: In New York, the current temperature is 23°C with a 10 km/h wind. The upcoming days will see temperatures from 18 to 26°C with light rain."
    )
},
{
    "question": "Peux-tu me donner la météo pour Berlin ?",
    "response": (
        "Action: weather_tool(city_name='Berlin')\n"
        "Observation: Météo actuelle à Berlin : 20°C, vent 9 km/h.\n"
        "Prévisions :\n"
        "2025-08-31 : Max 23°C / Min 16°C / Pluie 0 mm\n"
        "2025-09-01 : Max 22°C / Min 15°C / Pluie 0 mm\n"
        "2025-09-02 : Max 21°C / Min 14°C / Pluie 1 mm\n"
        "Final Answer: À Berlin, la température actuelle est de 20°C avec un vent de 9 km/h. Les prochains jours seront compris entre 14 et 23°C avec très peu de pluie."
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