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
st.set_page_config(page_title="Datacrumbs Chatbot", page_icon="🤖")

# Simple UI
st.title("Datacrumbs Chatbot")
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
    
    # Generate response using website content and Gemini
    with st.chat_message("assistant"):
        if llm:
            try:
                # Create a helpful system message that uses website content but isn't overly restrictive
                if website_content:
                    system_msg = SystemMessage(content=f"""
You are a helpful virtual assistant for Datacrumbs. Use the following website information to answer questions about Datacrumbs courses, services, and information. 

If you have relevant information from the website content below, use it to provide a helpful answer. If the specific information isn't available in the website content, you can provide general helpful responses while mentioning that for detailed information they should visit datacrumbs.org.

DATACRUMBS WEBSITE CONTENT:
{website_content}

Be helpful, friendly, and informative in your responses.
""")
                else:
                    system_msg = SystemMessage(content="""
You are a helpful virtual assistant for Datacrumbs. Answer questions about data science, courses, and learning as best you can. 
For specific Datacrumbs information, direct users to visit datacrumbs.org or contact help@datacrumbs.org.
""")
                
                messages = [system_msg, HumanMessage(content=prompt)]
                response = llm(messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                fallback_msg = "I'm having trouble accessing my knowledge right now. Please visit datacrumbs.org for information about our courses and services."
                st.write(fallback_msg)
                st.session_state.messages.append(AIMessage(content=fallback_msg))
        else:
            error_msg = "API configuration needed. Please contact help@datacrumbs.org for assistance."  
            st.write(error_msg)
            st.session_state.messages.append(AIMessage(content=error_msg))
