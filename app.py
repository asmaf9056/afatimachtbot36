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
    
    # More specific enrollment intent detection
    def wants_to_enroll(text):
        text_lower = text.lower()
        
        # Strong enrollment intent phrases
        strong_intent = [
            "i want to enroll",
            "i want to register",
            "i want to sign up",
            "i want to join",
            "how do i enroll",
            "how do i register", 
            "how do i sign up",
            "how do i join",
            "can i enroll",
            "can i register",
            "can i sign up",
            "can i join",
            "let me enroll",
            "let me register",
            "help me enroll",
            "help me register",
            "start enrollment",
            "begin enrollment",
            "proceed with enrollment",
            "ready to enroll",
            "ready to register"
        ]
        
        # Check for strong intent first
        if any(phrase in text_lower for phrase in strong_intent):
            return True
            
        # Check for action words + course words
        action_words = ["take", "join", "start", "begin", "do"]  
        course_words = ["course", "bootcamp", "program", "training"]
        
        has_action = any(word in text_lower for word in action_words)
        has_course = any(word in text_lower for word in course_words)
        
        if has_action and has_course:
            # Additional check - avoid informational questions
            info_words = ["what", "how", "when", "where", "why", "tell me", "explain", "about"]
            is_info_question = any(word in text_lower for word in info_words)
            
            # Only return True if it's not clearly an informational question
            return not is_info_question
            
        return False
    
    user_wants_to_enroll = wants_to_enroll(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if llm:
            try:
                system_msg = SystemMessage(content=f"""
You are a helpful virtual assistant for Datacrumbs. Use this information:

{datacrumbs_info}

Answer questions about courses and data science topics helpfully.

Only if the user explicitly expresses intent to enroll, register, or join a course (not just asking about enrollment), mention that you can help them with the enrollment form.
""")
                
                messages = [system_msg, HumanMessage(content=prompt)]
                response = llm(messages)
                
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
                
                # Show enrollment button only for clear enrollment intent
                if user_wants_to_enroll:
                    if st.button("📝 Fill Enrollment Form"):
                        st.session_state.show_enrollment = True
                        st.rerun()
                
            except Exception as e:
                st.write("I can help you with information about Datacrumbs courses.")
                if user_wants_to_enroll:
                    st.write("I can also help you with enrollment if you're ready to join a course.")
                    if st.button("📝 Fill Enrollment Form"):
                        st.session_state.show_enrollment = True
                        st.rerun()
        else:
            # Fallback without API
            st.write("I can help you with information about Datacrumbs courses.")
            if user_wants_to_enroll:
                st.write("I can also help you with enrollment if you're ready to join a course.")
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
