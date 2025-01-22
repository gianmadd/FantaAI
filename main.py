import json
import os

from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()
QROQ_API_KEY = os.getenv("QROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {"api_key": GEMINI_API_KEY, "model": "gemini-pro"},
    "verbose": True,
    "headless": False,
}


smart_scraper_graph = SmartScraperGraph(
    prompt="""
        Extract the name of all the teams and the corresponding link to the team page in the provided web page. 
        """,
    source="https://www.transfermarkt.it/serie-a/startseite/wettbewerb/IT1",
    config=graph_config,
)

# Run the pipeline
result = smart_scraper_graph.run()

# save result in txt file
with open("result.txt", "w") as f:
    f.write(str(result))

# save result in json file
with open("result.json", "w") as f:
    json.dump(result, f, indent=4)
