from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
import os
import openai
from dotenv import find_dotenv, load_dotenv
import requests
import json
import streamlit as st

def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Autonomous researcher - Twitter threads", page_icon=":bird:")

    st.header("Autonomous researcher - Twitter threads :bird:")
    openaiapi = st.text_input("OpenAI API Key")
    query = st.text_input("Topic of twitter thread")





if __name__ == '__main__':
    main()