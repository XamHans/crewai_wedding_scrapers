import os
from typing import List, Optional

import requests
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SeleniumScrapingTool, SerperDevTool
from langchain.tools import Tool
from pydantic import BaseModel, HttpUrl


# [Keep your existing Pydantic models here]
class Location(BaseModel):
    city: str
    state: str

class ContactInformation(BaseModel):
    phone: Optional[str]
    email: Optional[str]
    website: HttpUrl

class SocialMediaLinks(BaseModel):
    instagram: Optional[HttpUrl]

class ServiceProviderDetails(BaseModel):
	full_name: str
	description: str
	type_of_service: str
	location: Location
	contact_information: ContactInformation
	social_media_links: SocialMediaLinks
	price_packages: str
    
search_tool = SerperDevTool()
scrape_tool = SeleniumScrapingTool()

def validate_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"URL is valid and accessible: {url}"
        else:
            return f"URL returned a non-200 status code: {url}"
    except requests.RequestException:
        return f"URL is not accessible or invalid: {url}"

url_validation_tool = Tool(
    name="URL Validator",
    func=validate_url,
    description="Validates if a given URL is accessible and returns a 200 status code."
)

@CrewBase
class WeddingScrapersCrew():
    """WeddingScrapers crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'



    @agent
    def content_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config['content_scraper'],
            verbose=True,
            memory=True,
            tools=[scrape_tool],
        )

    @agent
    def data_structurer(self) -> Agent:
        return Agent(
            config=self.agents_config['data_structurer'],
            verbose=True,
            memory=True,
        )



    @task
    def scrape_provider_details_task(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_provider_details'],
            agent=self.content_scraper()
        )

    @task
    def structure_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['structure_data'],
            agent=self.data_structurer(),
            output_json=ServiceProviderDetails,
            output_file="bavarian_wedding_service_providers.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the WeddingScrapers crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            memory=True,
            process=Process.sequential,
            verbose=2,
        )