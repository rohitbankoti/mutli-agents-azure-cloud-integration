'''
Web scraping and sentiment extraction module
This module integrate with firecrawl api to act as eye of the system
it searches for qualitative data news, analyst opinions and market rumours


class SentimentSearchTool : Searches the web for recent news articles

'''

from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from firecrawl import FirecrawlApp
from src.shared.config import settings

# Input Schema

class FireCrawlSearchInput(BaseModel):
    query : str = Field(..., description="The search query string (e.g. NVDA recent analysis ratings)")

# Tool definition

class SentimentSearchTool(BaseTool):
    '''
    perform semantic web search and return scraped content
    use firecrawl, extract full page content in markdown format
    '''
    name : str = "Seach Stock News"
    description : str = ("Searches the web for the latest news, analyst ratings, surrounding market sentiments and return summary of top 3 relevant articles")

    args_schema : type[BaseModel] = FireCrawlSearchInput

    def _run(self, query: str) ->str :
        """
        executes search via firecrawl
        Args : query (str) : search topic
        returns : markdown string format content of top search results
        """

        if not settings.firecrawl_api_key: 
            return "Error : FIRECRAWL API KEY is missing in configuration"
        
        try: 
            app = FirecrawlApp(api_key=settings.firecrawl_api_key)

            #perform the web search : limit results to 3

            results = app.search(query=query, limit =3, scrape_options = {"formats" : ["markdown"]})

            return str(results)


        except Exception as e:
            return f"Error executing the Firecrawl search for query"    
