import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Page config MUST be first
st.set_page_config(page_title="Datacrumbs Chatbot", page_icon="🤖")

# Load API key from secrets or environment
try:
    # Try secrets first
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    # Fall back to environment variable
    import os
    api_key = os.getenv("GOOGLE_API_KEY")

# Initialize components
if api_key:
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.5
        )
        
        # Initialize embeddings for better document search
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        st.success("✅ Gemini API connected successfully!")
        
    except Exception as e:
        st.error(f"❌ Error initializing Gemini API: {str(e)}")
        llm = None
        embeddings = None
else:
    st.error("❌ GOOGLE_API_KEY not found in secrets or environment variables.")
    llm = None
    embeddings = None

# Load and process website content with better LangChain usage
@st.cache_resource
def create_vector_store():
    if not api_key:
        return None
        
    try:
        # Load website content
        loader = WebBaseLoader("https://datacrumbs.org/")
        documents = loader.load()
        
        # Better text splitting
        text_splitter = CharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separator="\n"
        )
        docs = text_splitter.split_documents(documents)
        
        # Create vector store for better search
        vector_store = FAISS.from_documents(docs, embeddings)
        return vector_store
        
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

# Initialize vector store
vector_store = create_vector_store()

# LangChain Memory for conversation
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# Create a proper prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful virtual assistant for Datacrumbs, a data science training institute.

Context from Datacrumbs website:
{context}

Based on the context above, please answer the following question about Datacrumbs courses, services, or general data science topics.

If the information isn't available in the context, mention that users can visit datacrumbs.org for more details.

Question: {question}

Answer:"""
)

# Fallback content if vector store fails
fallback_content = """
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

# UI
st.title("🤖 Datacrumbs AI Assistant")
st.subheader("Powered by LangChain & Gemini")

if vector_store:
    st.success(f"✅ Loaded website content with vector search enabled!")
else:
    st.warning("⚠️ Using fallback content. Vector search disabled.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    role = "assistant" if isinstance(message, AIMessage) else "user"
    with st.chat_message(role):
        st.write(message.content)

# Chat input
prompt = st.chat_input("Ask me about Datacrumbs courses, data science, or anything else...")

if prompt:
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if llm:
            try:
                if vector_store:
                    # Use LangChain's ConversationalRetrievalChain for better responses
                    qa_chain = ConversationalRetrievalChain.from_llm(
                        llm=llm,
                        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
                        memory=st.session_state.memory,
                        return_source_documents=True
                    )
                    
                    result = qa_chain({"question": prompt})
                    response_text = result["answer"]
                    
                else:
                    # Fallback to simple prompt with context
                    context_prompt = prompt_template.format(
                        context=fallback_content,
                        question=prompt
                    )
                    
                    response = llm([HumanMessage(content=context_prompt)])
                    response_text = response.content
                
                st.write(response_text)
                st.session_state.messages.append(AIMessage(content=response_text))
                
            except Exception as e:
                st.error(f"API Error: {str(e)}")
                # Basic fallback response
                basic_response = f"""
I can help with basic information about Datacrumbs:

Datacrumbs offers data science and analytics training including:
- Data Science & Analytics Bootcamps
- Python, SQL, and Excel courses  
- GenAI (Generative AI) training
- Business Intelligence courses

Features: hands-on projects, certifications, career placement assistance.

For complete details, visit datacrumbs.org or contact help@datacrumbs.org.

Your question: "{prompt}"
"""
                st.write(basic_response)
                st.session_state.messages.append(AIMessage(content=basic_response))
        else:
            # No API available
            st.error("❌ API not configured. Please add your GOOGLE_API_KEY to secrets.")

# Sidebar with LangChain info
with st.sidebar:
    st.markdown("### 🔧 LangChain Features Used:")
    st.markdown("""
    - **Document Loading**: WebBaseLoader
    - **Text Splitting**: Intelligent chunking  
    - **Vector Search**: FAISS embeddings
    - **Memory**: Conversation history
    - **Chains**: Q&A with retrieval
    - **Prompt Templates**: Structured prompts
    """)
    
    if vector_store:
        st.success("✅ Vector search active")
    else:
        st.warning("⚠️ Vector search disabled")
