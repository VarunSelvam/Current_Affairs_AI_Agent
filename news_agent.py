#-------------------------------------------------------------------------------------------
# Import statements
import datetime as dt
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from agent_tools import news_search_tool, news_summary_report_tool,news_headline_tool
#-------------------------------------------------------------------------------------------

# Extract Current Time and 7 days beforehand for a week

current_date = dt.datetime.now()
seven_days_ago = current_date - dt.timedelta(days=7)

current_date = str(current_date)
current_date = current_date[0:10]

seven_days_ago = str(seven_days_ago)
seven_days_ago = seven_days_ago[0:10]

# Loading API Keys
os.chdir("..")
upper_path = os.getcwd()
env_path = os.path.join(upper_path,"Environment_Variables",".env")
load_dotenv(dotenv_path=env_path)

# Specifying format of the news report
class NewsReport(BaseModel):
    news_topic: str
    report:str
    tools_utilized: (str)

# Call AI Model and intialize it.
# First Agent, Anthropic to summarize the news
claude = ChatAnthropic(model="claude-3-5-haiku-20241022")

# Check that model works
# response = Anthropic.invoke("What is the meaning of life?")
# print(response)

# Create Python Object
python_parser = PydanticOutputParser(pydantic_object=NewsReport)

# Messaging Template

task_description = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a current event researcher. You'll research any current events or news related to the inquiry from the internet starting from {week_beginning} to {week_end}.
            Afterwards, you'll write a summary of the current event.
            Wrap the output in this format and provide no other text\n{report_format}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"), # Can hold more than one variable like {name}, {query}.
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(report_format=python_parser.get_format_instructions(),week_beginning = seven_days_ago, week_end = current_date)

# Give access to the new_search, so that this AI Agent can search the web.
tool_kit = [news_search_tool,news_headline_tool]
# Intialize Agent
news_agent = create_tool_calling_agent( # Creates the agent
    llm=claude,
    prompt=task_description,
    tools=tool_kit
)

# Actually execute the agent
news_executor = AgentExecutor(agent=news_agent,tools=tool_kit,verbose=True) # Agent will automatically fill out {chat history} and {agent_scratchpad}

# Prompt the user for a query
user_question = input("Hello, I can help answer current event questions. Please ask: ")

# Store query in an unfiltered JSON format (Actually run the agent)
unfiltered_response = news_executor.invoke({"query": user_question})

# Use try-except to catch errors and clean the response
try:
    cleaned_response = python_parser.parse(unfiltered_response.get('output')[0]["text"])
    print(cleaned_response)
    # Create a Dictionary to store news summary. This will be fed into the next LLM which is ChatGPT
    anthropic_news_summmary = dict()
    anthropic_news_summmary[cleaned_response.news_topic] = cleaned_response.report
except Exception as e:
    print("An error occurred for Claude:", e)
    print("Pursuing Alternative Path instead")
    anthropic_news_summmary = repr(unfiltered_response)
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
# ChatGPT to edit the summary and approve it afterwards

chat_gpt = ChatOpenAI(model="gpt-4.1-2025-04-14")
# Check that model works
# response = chat_gpt.invoke("What is the meaning of life?")
# print(response)

class NewsReportEdit(BaseModel):
    news_topic: str
    edited_report:str
    tools_utilized: (str)

python_news_editor_parser = PydanticOutputParser(pydantic_object=NewsReportEdit)

# Messaging Template

news_editor_task = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a news editor who must decide whether to approve or edit the news summary provided by a news agent.
            You may also use any internet search tools to do additional research for editing, if you think that additional info is required.
            However any additional research must be relevant from this date: {week_beg} to this date: {week_finish}
            REQUIRED - Once you are done making edits or approving the summary, you must MANDATORILY save the news summary w/all of its contents to this computer. If you decided to edit the news summary, then save ONLY the edited new summary to this computer.
            REQUIRED - Use this tool "news_summary_report_tool" to write the summary to the computer.
            Wrap the output in this format and provide no other text\n{edited_report_format} 
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(week_beg = seven_days_ago,week_finish = current_date,edited_report_format=python_news_editor_parser.get_format_instructions())

news_editor_tool_kit = [news_search_tool, news_summary_report_tool]
news_editor_agent = create_tool_calling_agent( # Creates the agent
    llm=chat_gpt,
    prompt=news_editor_task,
    tools=news_editor_tool_kit
)

news_editor_executor = AgentExecutor(agent=news_editor_agent,tools=news_editor_tool_kit,verbose=True) # Agent will automatically fill out {chat history} and {agent_scratchpad}

news_editor_unfiltered_response = news_editor_executor.invoke({"query": anthropic_news_summmary})

official_news_summary = news_editor_unfiltered_response.get("query")

for index in enumerate(official_news_summary):
    a = index

text_summary = a[1]

try:
    news_editor_cleaned_response = official_news_summary[text_summary]
    print(news_editor_cleaned_response) # If you want it in Console
except Exception as e:
    print("An error occurred for ChatGPT:", e)
