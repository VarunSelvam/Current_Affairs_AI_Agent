from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from datetime import datetime

# Input news summary into a text file
def current_events_summary(data: str, file: str = "news_summary.txt"): 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cleaned_text = f"--- News Summary ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(file, "a", encoding="utf-8") as f:
        f.write(cleaned_text)


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
