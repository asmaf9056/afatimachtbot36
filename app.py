import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Page config MUST be first
st.set_page_config(page_title="Datacrumbs Chatbot", page_icon="🤖")

# Load API key from secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]  # Changed from GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",  # Changed from gemini-pro
        google_api_key=api_key,
        temperature=0.5
    )
    st.success("✅ Gemini API connected successfully!")
except KeyError:
    st.error("❌ GOOGLE_API_KEY not found in secrets. Please add it to your secrets.toml file.")
    llm = None
except Exception as e:
    st.error(f"❌ Error initializing Gemini API: {str(e)}")
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
    st.success(f"✅ Loaded {len(website_docs)} chunks from Datacrumbs website!")
else:
    st.warning("⚠️ Could not load website content. Using fallback data.")
    # Fallback content about Datacrumbs
    website_content = """
    DATACRUMBS INFORMATION:
    
    Datacrumbs is a data science and analytics training institute.
    
    COURSES OFFERED:
    - Data Science Bootcamp
    - Data Analytics Bootcamp  
    - Business Intelligence Bootcamp
    - GenAI Bootcamp (Generative AI)
    - Ultimate Python Bootcamp
    - SQL Zero to Hero
    - Excel for Everyone
    
    FEATURES:
    - Industry-ready curriculum
    - Hands-on projects
    - Certification upon completion
    - Internship opportunities
    - Career placement assistance
    - Live mentorship sessions
    - Community support
    
    CONTACT:
    Website: datacrumbs.org
    Email: help@datacrumbs.org
    """

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
                # Create a helpful system message
                system_msg = SystemMessage(content=f"""
You are a helpful virtual assistant for Datacrumbs. Use the following information to answer questions about Datacrumbs courses, services, and general data science topics.

DATACRUMBS INFORMATION:
{website_content}

Answer questions helpfully using this information. If asked about specific details not covered above, mention that users can visit datacrumbs.org for more information.
""")
                
                messages = [system_msg, HumanMessage(content=prompt)]
                response = llm(messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
                
            except Exception as e:
                st.error(f"Gemini API Error: {str(e)}")
                # Provide a basic response without API
                basic_response = f"""
I can help you with information about Datacrumbs! Here's what I know:

Datacrumbs offers various data science and analytics courses including:
- Data Science Bootcamp
- Data Analytics Bootcamp
- Python and SQL courses
- GenAI (Generative AI) training

For detailed information about pricing, schedules, and enrollment, please visit datacrumbs.org or contact help@datacrumbs.org.

Your question was: "{prompt}"
"""
                st.write(basic_response)
                st.session_state.messages.append(AIMessage(content=basic_response))
        else:
            # Provide basic response when API is not configured
            basic_response = f"""
I can help with basic information about Datacrumbs:

Datacrumbs offers data science and analytics training with courses like:
- Data Science Bootcamp
- Data Analytics Bootcamp  
- Python, SQL, and Excel courses
- GenAI (Generative AI) training

Features include hands-on projects, certifications, and career placement assistance.

For complete details, visit datacrumbs.org or contact help@datacrumbs.org.

Your question: "{prompt}"
"""
            st.write(basic_response)
            st.session_state.messages.append(AIMessage(content=basic_response))
