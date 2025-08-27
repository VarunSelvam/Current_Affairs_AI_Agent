from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from newsapi import NewsApiClient
import datetime as dt
import os
from dotenv import load_dotenv
import json
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# Input news summary into a text file
def current_events_summary(data: str, file: str = "news_summary.txt"): 
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cleaned_text = f"--- News Summary ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(file, "a", encoding="utf-8") as f:
        f.write(cleaned_text)
    print("File Saved Sucessfully")

# Wrap this function into a tool that the LLM's can access.
news_summary_report_tool = Tool(
    name = "save_to_text_file",
    func = current_events_summary, 
    description="write the final news summary report with the report title and ALL of the news reports's content into a text file." 
)


# This is a tool that we can allow our agent to use Duck Duck Go for searching
search = DuckDuckGoSearchRun()
news_search_tool = Tool(
    name = "news_search", 
    func = search.run,
    description="Search the web for current events or news" 
)

# Utilize news api for news search
def news_headlines(news_type: str,search_terms: str):
    news_type = news_type.lower()
    current_date = dt.datetime.now()
    seven_days_ago = current_date - dt.timedelta(days=7)

    current_date = str(current_date)
    current_date = current_date[0:10]

    seven_days_ago = str(seven_days_ago)
    seven_days_ago = seven_days_ago[0:10]

    os.chdir('..')
    upper_path = os.getcwd()
    env_path = os.path.join(upper_path,"Environment_Variables",".env")

    load_dotenv(dotenv_path=env_path)
    news_api_key = os.getenv("api_key")
    newsapi = NewsApiClient(api_key=news_api_key)
    sources = newsapi.get_sources()

    category = sources['sources']
    technology = []
    business  = []
    entertainment = []
    sports = []
    general = []
    health = []
    science = []
    # Print out the category for every news source
    for i in range(0,len(category)):
        news_source_info = sources['sources'][i].items()
        news_source_info = list(news_source_info)
        news_category = news_source_info[4][1]
        if news_category == 'technology':
            technology.append(news_source_info)
        elif news_category == 'business':
            business.append(news_source_info)
        elif news_category == 'entertainment':
            entertainment.append(news_source_info)
        elif news_category == 'sports':
            sports.append(news_source_info)
        elif news_category == 'general':
            general.append(news_source_info)
        elif news_category == 'health':
            health.append(news_source_info)
        elif news_category == 'science':
            science.append(news_source_info)

    def domain_extractor(category_name):
        https = "https://"
        http = 'http://'
        www = 'www.'
        
        domain_list = []

        for i in range(0,len(category_name)):
            url = category_name[i][3][1]
            if https in url and www in url:
                url = url.replace(https,"")
                url = url.replace(www,"")
                domain_list.append(url)
            elif http in url and www in url:
                url = url.replace(http,"")
                url = url.replace(www,"")
                domain_list.append(url)
            elif https in url:
                url = url.replace(https,"")
                domain_list.append(url)
            elif http in url:
                url = url.replace(http,"")
                domain_list.append(url)
        
        domain_string = ",".join(domain_list)
        return domain_string

    # Specify User Domain
    if news_type == 'technology':
        domain_type = domain_extractor(technology)
    elif news_type == 'business':
        domain_type = domain_extractor(business)
    elif news_type == 'entertainment':
        domain_type = domain_extractor(entertainment)
    elif news_type == 'sports':
        domain_type = domain_extractor(sports)
    elif news_type == 'general':
        domain_type = domain_extractor(general)
    elif news_type =='health':
        domain_type = domain_extractor(health)
    elif news_type == 'science':
        domain_type = domain_extractor(science)

    all_articles = newsapi.get_everything(qintitle=search_terms,
                                        domains = domain_type,
                                        from_param=seven_days_ago,
                                        to=current_date,
                                        language='en',
                                        sort_by='relevancy'
                                        )
    
    json_format = json.dumps(all_articles)
    return json_format



class NewsInput(BaseModel):
    news_type: str = Field(description="News category: technology, business, entertainment, sports, general, health, or science")
    search_terms: str = Field(description="Keywords to search for in headlines")

news_headline_tool = StructuredTool.from_function(
    func=news_headlines,
    name="news_headlines",
    description="Search news headlines by category and keywords",
    args_schema=NewsInput
)
