import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Page config
st.set_page_config(page_title="Datacrumbs Chatbot", page_icon="🤖")

# Load API key
api_key = None
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    pass

# Initialize LLM
if api_key:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.5
        )
    except:
        llm = None
else:
    llm = None

# Datacrumbs info
datacrumbs_info = """
DATACRUMBS COURSES:
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

CONTACT: datacrumbs.org | help@datacrumbs.org
"""

# Simple UI
st.title("Datacrumbs Chatbot")
st.subheader("I'll be your virtual assistant today...")

# Initialize states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_enrollment" not in st.session_state:
    st.session_state.show_enrollment = False

# Display chat messages
for message in st.session_state.messages:
    role = "assistant" if isinstance(message, AIMessage) else "user"
    with st.chat_message(role):
        st.write(message.content)

# Chat input
prompt = st.chat_input("*your question here...*")

if prompt:
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Check if user wants to enroll
    enrollment_keywords = ["enroll", "enrollment", "register", "sign up", "join course", "pay fee", "reserve spot", "book course"]
    wants_to_enroll = any(keyword in prompt.lower() for keyword in enrollment_keywords)
    
    # Generate response
    with st.chat_message("assistant"):
        if llm:
            try:
                system_msg = SystemMessage(content=f"""
You are a helpful virtual assistant for Datacrumbs. Use this information:

{datacrumbs_info}

If user asks about enrollment, registration, or wants to join a course, tell them you can help them with enrollment and ask if they'd like to fill out the enrollment form.

Answer other questions about courses and data science topics helpfully.
""")
                
                messages = [system_msg, HumanMessage(content=prompt)]
                response = llm(messages)
                
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
                
                # Show enrollment button if user wants to enroll
                if wants_to_enroll:
                    if st.button("📝 Fill Enrollment Form"):
                        st.session_state.show_enrollment = True
                        st.rerun()
                
            except Exception as e:
                st.write("I can help you with information about Datacrumbs courses. For enrollment, I can show you the enrollment form.")
                if wants_to_enroll:
                    if st.button("📝 Fill Enrollment Form"):
                        st.session_state.show_enrollment = True
                        st.rerun()
        else:
            # Fallback without API
            st.write("I can help you with information about Datacrumbs courses and enrollment.")
            if wants_to_enroll:
                if st.button("📝 Fill Enrollment Form"):
                    st.session_state.show_enrollment = True
                    st.rerun()

# Enrollment Form
if st.session_state.show_enrollment:
    st.markdown("---")
    st.header("🎓 Enrollment Form")
    st.subheader("Reserve Your Spot Today!")
    
    with st.form("enrollment_form"):
        # Personal Information
        st.markdown("**Personal Information**")
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        email = st.text_input("Email Address *", placeholder="your.email@example.com")
        whatsapp = st.text_input("WhatsApp Number *", placeholder="+92 300 1234567")
        
        # Address
        st.markdown("**Address**")
        address = st.text_area("Complete Address *", placeholder="House #, Street, Area, City")
        
        # Course Selection
        st.markdown("**Course Selection**")
        course = st.selectbox("Select Course *", [
            "Select a course...",
            "Data Science Bootcamp",
            "Data Analytics Bootcamp",
            "Business Intelligence Bootcamp", 
            "GenAI Bootcamp (Generative AI)",
            "Ultimate Python Bootcamp",
            "SQL Zero to Hero",
            "Excel for Everyone"
        ])
        
        # Additional Info
        st.markdown("**Additional Information**")
        experience = st.selectbox("Your Experience Level", [
            "Beginner (No prior experience)",
            "Intermediate (Some experience)", 
            "Advanced (Experienced professional)"
        ])
        
        motivation = st.text_area("Why do you want to join this course?", 
                                placeholder="Tell us about your goals and motivation...")
        
        # Terms
        terms = st.checkbox("I agree to the terms and conditions and enrollment policies *")
        
        # Submit
        submitted = st.form_submit_button("🎯 Submit Enrollment & Pay Fee")
        
        if submitted:
            if not all([name, email, whatsapp, address, course != "Select a course...", terms]):
                st.error("❌ Please fill all required fields marked with *")
            else:
                st.success("✅ Enrollment submitted successfully!")
                st.balloons()
                st.markdown(f"""
                **Enrollment Details:**
                - **Name:** {name}
                - **Course:** {course}
                - **Contact:** {whatsapp}
                
                **Next Steps:**
                1. You will receive a confirmation email shortly
                2. Payment link will be sent to your WhatsApp
                3. Course details will be shared after payment
                
                **Contact:** help@datacrumbs.org for any queries
                """)
                
                # Reset form
                if st.button("🔄 Submit Another Enrollment"):
                    st.session_state.show_enrollment = False
                    st.rerun()
    
    # Close form button
    if st.button("❌ Close Enrollment Form"):
        st.session_state.show_enrollment = False
        st.rerun()
   
