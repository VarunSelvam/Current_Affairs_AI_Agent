from newsapi import NewsApiClient
import datetime as dt
import os
from dotenv import load_dotenv

# Getting current week
#------------------------------------------------------
current_date = dt.datetime.now()
seven_days_ago = current_date - dt.timedelta(days=7)

current_date = str(current_date)
current_date = current_date[0:10]

seven_days_ago = str(seven_days_ago)
seven_days_ago = seven_days_ago[0:10]
#------------------------------------------------------
# Getting the Environment Variable
os.chdir('..')
upper_path = os.getcwd()
env_path = os.path.join(upper_path,"Environment_Variables",".env")

load_dotenv(dotenv_path=env_path)
#---------------------------------------------------------

# Setup News API
# Init
news_api_key = os.getenv("api_key")
newsapi = NewsApiClient(api_key=news_api_key)

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q='bitcoin',
                                          sources='bbc-news,the-verge')


# /v2/top-headlines
all_articles = newsapi.get_everything(q='Japan',
                                      # domains ='the-verge',
                                      from_param=seven_days_ago,
                                      to=current_date,
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)

sources = newsapi.get_sources()

print(all_articles)
print(len(all_articles['articles']))
print(sources) 
print(top_headlines)
print(f"Date range: {seven_days_ago} to {current_date}")
# ----------------------------------------------------------

# Checking API Key to ensure it works
# ----------------------------------------------------------
try:
    test = newsapi.get_everything(q='Japan', page_size=1)
    print("API Key Status:", "Working" if test['status'] == 'ok' else "Issue")
    print("Total Results:", test.get('totalResults', 'N/A'))
    print("Articles Found:", len(test.get('articles', [])))
except Exception as e:
    print("API Error:", str(e))

# Test 2: Check your current limits
print("API Key Info - check your NewsAPI dashboard for current plan limits")
# ----------------------------------------------------------

# Extract the Category from the news
# ----------------------------------------------------------

# Check how many sources are there
sources = newsapi.get_sources()
print(f"Total sources: {len(sources['sources'])}") # 127 total sources

# Way 1 to extract the category
type(sources)
sources['sources'] # C
sources['sources'][0]
sources['sources'][1]
a = sources['sources'][0].items()
a = list(a)

print(a)
a[4][1]

category = sources['sources']
len(category)


category_list = []
technology = []
business  = []
entertainment = []
sports = []
general = []
health = []
science = []
# Print out the category for every news source
for i in range(0,len(category)):
    a = sources['sources'][i].items()
    a = list(a)
    b = a[4][1]
    category_list.append(b)
    if b == 'technology':
        technology.append(a)
    elif b == 'business':
        business.append(a)
    elif b == 'entertainment':
        entertainment.append(a)
    elif b == 'sports':
        sports.append(a)
    elif b == 'general':
        general.append(a)
    elif b == 'health':
        health.append(a)
    elif b == 'science':
        science.append(a)

len(technology) + len(business) + len(entertainment) + len(sports) + len(general) + len(health) + len(science)
len(category_list)

print(f'technology: {len(technology)}\nbusiness: {len(business)}\nentertainment: {len(entertainment)}\nsports: {len(sports)}\ngeneral: {len(general)}\nhealth: {len(health)}\nscience: {len(science)}')

# Way 2
# Print all source IDs and names
source_list = []
for source in sources['sources']: # Convert to a list 
    a = f"ID: {source['id']}, Name: {source['name']}, Category: {source['category']}"
    source_list.append(a)

# Print the source list and check that all the sources and the number of sources is the same. Should be 127
print(source_list)
len(source_list) # Should be 127

#-----------------------------------------------------------------------------
# Extract the urls which we'll use as domains for each category. (This will be done from Way 1)
technology[0]
one_url = technology[0][3][1]
one_url.index("https://")
one_url.find("https://")
one_url= one_url.replace("https://","")

# Automate this for all urls
technology_domains = []
https = "https://"
http = 'http://'
www = 'www.'
for i in range(0,len(technology)):
    url = technology[i][3][1]
    if https in url and www in url:
        url = url.replace(https,"")
        url = url.replace(www,"")
        technology_domains.append(url)
    elif http in url and www in url:
        url = url.replace(http,"")
        url = url.replace(www,"")
        technology_domains.append(url)
    elif https in url:
        url = url.replace(https,"")
        technology_domains.append(url)
    elif http in url:
        url = url.replace(http,"")
        technology_domains.append(url)

technology_domains = ",".join(technology_domains)

# Convert automation into function
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
    
    domain_list = ",".join(domain_list)
    return domain_list

# Run Function for the categories
technology_domains = domain_extractor(category_name=technology)
technology_domains = technology_domains.split(",")

business_domains = domain_extractor(category_name=business)
business_domains = business_domains.split(",")

entertainment_domains = domain_extractor(entertainment)
entertainment_domains = entertainment_domains.split(',')

sports_domains = domain_extractor(sports)
sports_domains = sports_domains.split(',')

general_domains = domain_extractor(general)
general_domains = general_domains.split(',')

health_domains = domain_extractor(health)
health_domains = health_domains.split(',')

science_domains = domain_extractor(science)
science_domains = science_domains.split(',')

len(technology_domains) + len(business_domains) + \
len(entertainment_domains) + len(sports_domains) + \
len(general_domains) + len(health_domains) + len(science_domains)

print(f'technology: {len(technology_domains)}\nbusiness: {len(business_domains)}\nentertainment: {len(entertainment_domains)}\nsports: {len(sports_domains)}\ngeneral: {len(general_domains)} \nhealth: {len(health_domains)} \nscience: {len(science_domains)}')


# Test if it works
all_articles = newsapi.get_everything(qintitle='Japan',
                                      domains = general_domains,
                                      from_param=seven_days_ago,
                                      to=current_date,
                                      language='en',
                                      sort_by='relevancy'
                                      )

print(all_articles)

top_headlines = newsapi.get_top_headlines(q='Japan',
                                          sources= general_domains)

print(top_headlines)

# ---------------------------------------------------------
# Create tool based of this function
from newsapi import NewsApiClient
import datetime as dt
import os
from dotenv import load_dotenv
import json

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

news_headlines("general","Japan")