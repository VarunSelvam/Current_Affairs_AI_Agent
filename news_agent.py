#-------------------------------------------------------------------------------------------
# Import statements
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from agent_tools import news_search_tool, new_summary_report_tool
#-------------------------------------------------------------------------------------------
# First Agent, Anthropic to summarize the news

# Loading API Keys
load_dotenv()

# Specifying format of the news report
class NewsReport(BaseModel):
    news_topic: str
    report:str
    tools_utilized: (str)

# Call AI Model and intialize it.
anthropic = ChatAnthropic(model="claude-3-5-haiku-20241022")

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
            You are a current event researcher. You'll research any current events or news from the internet.
            Afterwards, you'll write a summary of the current event.
            Wrap the output in this format and provide no other text\n{report_format} 
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"), # Can hold more than one variable like {name}, {query}.
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(report_format=python_parser.get_format_instructions())

# Give access to the new_search, so that this AI Agent can search the web.
tool_kit = [news_search_tool]
# Intialize Agent
news_agent = create_tool_calling_agent( # Creates the agent
    llm=anthropic,
    prompt=task_description,
    tools=tool_kit
)

# Actually execute the agent
news_executor = AgentExecutor(agent=news_agent,tools=tool_kit,verbose=True) # Agent will automatically fill out {chat history} and {agent_scratchpad}

# Prompt the user for a query
user_question = input("Hello, I can help answer current event questions. Please ask: ")

# Store query in an unfiltered JSON format
unfiltered_response = news_executor.invoke({"query": user_question})

# Use try-except to catch errors and clean the response
try:
    cleaned_response = python_parser.parse(unfiltered_response.get('output')[0]["text"])
    print(cleaned_response)
except Exception as e:
    print("An error occurred for Anthropic:", e)
#-------------------------------------------------------------------------------------------
# Create a Dictionary to store news summary. This will be fed into the next LLM which is ChatGPT
anthropic_new_summmary = dict()
anthropic_new_summmary[cleaned_response.news_topic] = cleaned_response.report

#-------------------------------------------------------------------------------------------
# ChatGPT to edit the summary and approve it afterwards

chat_gpt = ChatOpenAI(model="gpt-3.5-turbo")

# Check that model works
# response = chat_gpt.invoke("What is the meaning of life?")
# print(response)

load_dotenv()

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
            You have the final say, and regardless of what you decide, you must print the news summary.
            Wrap the output in this format and provide no other text\n{edited_report_format} 
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(edited_report_format=python_news_editor_parser.get_format_instructions())

news_editor_tool_kit = [news_search_tool, new_summary_report_tool]
news_editor_agent = create_tool_calling_agent( # Creates the agent
    llm=chat_gpt,
    prompt=news_editor_task,
    tools=news_editor_tool_kit
)

news_editor_executor = AgentExecutor(agent=news_editor_agent,tools=news_editor_tool_kit,verbose=True) # Agent will automatically fill out {chat history} and {agent_scratchpad}

news_editor_unfiltered_response = news_editor_executor.invoke({"query": anthropic_new_summmary})

try:
    news_editor_cleaned_response = python_parser.parse(news_editor_unfiltered_response.get('output')[0]["text"])
    print(news_editor_cleaned_response)
except Exception as e:
    print("An error occurred for chatGPT:", e)