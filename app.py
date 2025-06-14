import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Load API key from secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.5
    )
except:
    llm = None

# Load website content using WebBaseLoader
@st.cache_data
def load_website_content():
    try:
        loader = WebBaseLoader("https://datacrumbs.org/")
        documents = loader.load()
        
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(documents)
        return docs
    except:
        return None

# Get website content for context
website_docs = load_website_content()
website_content = ""
if website_docs:
    website_content = "\n".join([doc.page_content for doc in website_docs])

# Page config
st.set_page_config(page_title="Datacrumbs Virtual Assistant", page_icon="🤖")

# Simple UI
st.title("datacrumbs.org")
st.subheader("I'll be your virtual assistant today...")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    role = "assistant" if isinstance(message, AIMessage) else "user"
    with st.chat_message(role):
        st.write(message.content)

# Chat input with placeholder
prompt = st.chat_input("Your question here...")

if prompt:
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response only from website content
    with st.chat_message("assistant"):
        if llm and website_content:
            try:
                # Create a strict system message to only use website content
                system_msg = SystemMessage(content=f"""
You are a virtual assistant for Datacrumbs. You can ONLY answer questions using the information provided from the Datacrumbs website below. 

If a question cannot be answered from this website content, politely say that you can only provide information available on the Datacrumbs website and suggest they visit datacrumbs.org or contact help@datacrumbs.org for more details.

DATACRUMBS WEBSITE CONTENT:
{website_content}

Answer the user's question using only this information.
""")
                
                messages = [system_msg, HumanMessage(content=prompt)]
                response = llm(messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
                
            except Exception as e:
                fallback_msg = "I can only provide information available on the Datacrumbs website. Please visit datacrumbs.org or contact help@datacrumbs.org for more information."
                st.write(fallback_msg)
                st.session_state.messages.append(AIMessage(content=fallback_msg))
        else:
            fallback_msg = "I can only provide information available on the Datacrumbs website. Please visit datacrumbs.org or contact help@datacrumbs.org for more information."
            st.write(fallback_msg)
            st.session_state.messages.append(AIMessage(content=fallback_msg))
