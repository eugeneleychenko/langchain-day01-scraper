from langchain import LLMChain, PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
import os
# from dotenv import find_dotenv, load_dotenv
import requests
import json
import streamlit as st
from bs4 import BeautifulSoup

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def search(query):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': SERPAPI_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()

    print("Search Results: ", response_data)
    return response_data

def find_best_article_urls(response_data, query):
    # turn json into string
    response_str = json.dumps(response_data)

    # create llm to choose best articles
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=.7)
    template = """
    You are a world class journalist & researcher, you are extremely good at finding most relevant articles to certain topic;
    {response_str}
    Above is the list of search results for the query {query}.
    Please choose the best 3 articles from the list, return ONLY an array of the urls, do not include anything else; return ONLY an array of the urls, do not include anything else
    """

    prompt_template = PromptTemplate(
        input_variables=["response_str", "query"], template=template)

    article_picker_chain = LLMChain(
        llm=llm, prompt=prompt_template, verbose=True)

    urls = article_picker_chain.predict(response_str=response_str, query=query)

    # Convert string to list
    url_list = json.loads(urls)
    print(url_list)

    return url_list

def get_content_from_urls(urls):   
    contents = []  # Initialize an empty array to store the contents

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
    for url in urls:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("body")
        contents.append(body.get_text())  # Append the content to the array
    
    return contents

def generate_bullets(summaries, query):
    summaries_str = str(summaries)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=.7)
    template = """
    {summaries_str}

    You are a world class researcher, text above is some context about {query}
    Please write a reserach bullet point document about {query} using the text above, and following all rules below:
    1/ The points needs to be engaging, informative with good data
    2/ The bullets need to be cited.
    3/ The bullets needs to address the {query} topic very well
    4/ The bullets needs to speak to an investor that can take action on this advice.
    5/ The thread needs to be written in a way that is easy to read and understand
    6/ The thread needs to give audience actionable advice & insights too

    BULLET THREAD:
    """

    prompt_template = PromptTemplate(input_variables=["summaries_str", "query"], template=template)
    bullet_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

    bullet_thread = bullet_chain.predict(summaries_str=summaries_str, query=query)

    return bullet_thread

    

def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Google Scraper")
    st.header("Deep Dive on Interesting Topics")
    query = st.text_input("Enter topic")
    
   
    if query:
            print(query)
            st.write("Research this topic: ", query)
            # st.write("Grabbing content of: ", articles)
            
            #functions
            search_results = search(query)
            articles = find_best_article_urls(search_results, query)
            content = get_content_from_urls(articles)
            bullets = generate_bullets(content, query)

            with st.expander("Search Results"):
                st.json(search_results)
            with st.expander("Best Articles"):
                st.write(articles)
            with st.expander("Article Content"):
                st.write(content)
            with st.expander("Bullets"):
                st.write(bullets)





if __name__ == '__main__':
    main()