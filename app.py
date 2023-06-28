from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
import os
import openai
from dotenv import find_dotenv, load_dotenv
import requests
import json
import streamlit as st

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

    print("search results: ", response_data)
    return response_data

def find_best_article_urls(response_data, query):
    # turn json into string
    response_str = json.dumps(response_data)

    # create llm to choose best articles
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=.7)
    template = """
    You are a world class journalist & researcher, you are extremely good at find most relevant articles to certain topic;
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


def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Google Scraper", )

    st.header("Scrape Google results and returns them")
    # openaiapi = st.text_input("OpenAI API Key")
    query = st.text_input("Enter your query")
   
    if query:
            print(query)
            st.write("Searching Google for: ", query)
            
            #functions
            search_results = search(query)
            find_best_article_urls(search_results, query)

            with st.expander("search results"):
                st.json(search_results)
            with st.expander("best articles"):
                st.json(find_best_article_urls)





if __name__ == '__main__':
    main()