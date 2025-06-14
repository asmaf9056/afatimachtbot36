import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import time

# Page config
st.set_page_config(page_title="Datacrumbs Chatbot", page_icon="🤖")

# Load API key
api_key = None
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.warning("⚠️ Google API key not found. Using fallback responses.")

# Initialize LLM with better error handling
llm = None
if api_key:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.7,
            timeout=10  # Add timeout
        )
        # Test the connection
        test_msg = [SystemMessage(content="Test"), HumanMessage(content="Hello")]
        llm(test_msg)
        st.success("✅ AI assistant ready!")
    except Exception as e:
        st.error(f"❌ AI connection failed: {str(e)}")
        llm = None

# Datacrumbs info
datacrumbs_info = """
DATACRUMBS COURSES:
- Data Science Bootcamp: Complete program covering Python, ML, statistics, and real projects
- Data Analytics Bootcamp: Focus on data visualization, Excel, SQL, and business insights  
- Business Intelligence Bootcamp: Power BI, Tableau, data warehousing, and BI tools
- GenAI Bootcamp (Generative AI): ChatGPT, prompt engineering, AI tools, and automation
- Ultimate Python Bootcamp: From basics to advanced Python programming
- SQL Zero to Hero: Database management, queries, and data manipulation
- Excel for Everyone: Advanced Excel, formulas, pivot tables, and automation

FEATURES:
- Industry-ready curriculum designed by experts
- Hands-on projects with real datasets
- Professional certification upon completion
- Internship opportunities with partner companies
- Career placement assistance and job support
- Live mentorship sessions with industry professionals
- Flexible scheduling options
- Lifetime access to course materials

PRICING: Contact for current pricing and payment plans
CONTACT: 
- Website: datacrumbs.org 
- Email: help@datacrumbs.org
- WhatsApp support available
"""

# Fallback responses for when API is not available
def get_fallback_response(prompt):
    prompt_lower = prompt.lower().strip()
    
    # Helper 
    
    # Pricing questions
    elif any(word in prompt_lower for word in ["price", "cost", "fee", "payment"]):
        return "💰 **Pricing Information:**\nWe offer competitive pricing with flexible payment plans. Costs vary by course and duration. We also provide:\n- Early bird discounts\n- Student discounts\n- Installment payment options\n- Scholarship opportunities\n\nContact us at help@datacrumbs.org or fill out our enrollment form for current pricing!"
    
    # Duration questions
    elif any(word in prompt_lower for word in ["duration", "time", "long", "weeks", "months"]):
        return "⏰ **Course Duration:**\n- Data Science Bootcamp: 12-16 weeks\n- Data Analytics Bootcamp: 8-12 weeks\n- Business Intelligence: 10-14 weeks\n- GenAI Bootcamp: 6-8 weeks\n- Python Bootcamp: 8-10 weeks\n- SQL Zero to Hero: 4-6 weeks\n- Excel for Everyone: 3-4 weeks\n\nAll courses include flexible scheduling options and lifetime access to materials!"
    
    # Prerequisites questions
    elif any(word in prompt_lower for word in ["prerequisite", "requirement", "beginner", "experience"]):
        return "✅ **Prerequisites:**\nMost of our courses are designed for beginners! No prior experience required for:\n- Excel for Everyone\n- SQL Zero to Hero\n- Ultimate Python Bootcamp\n- GenAI Bootcamp\n\nFor Data Science and Analytics bootcamps, basic computer skills are helpful but we'll teach you everything from scratch. We welcome learners from all backgrounds!"
    
    # Certificate questions
    elif any(word in prompt_lower for word in ["certificate", "certification", "credential"]):
        return "🏆 **Certification:**\nYes! You'll receive an industry-recognized certificate upon successful completion of any bootcamp. Our certificates are:\n- Verified and authentic\n- Recognized by employers\n- Include your project portfolio\n- Boost your resume and LinkedIn profile\n- Demonstrate practical skills to employers"
    
    # Job/career questions
    elif any(word in prompt_lower for word in ["job", "career", "placement", "employment", "salary"]):
        return "💼 **Career Support:**\nWe provide comprehensive career assistance:\n- Resume building and optimization\n- Interview preparation and mock interviews\n- Job placement assistance with partner companies\n- LinkedIn profile optimization\n- Portfolio development guidance\n- Networking opportunities\n- Salary negotiation tips\n\nMany graduates land roles within 3-6 months of completion!"
    
    # Contact questions
    elif any(word in prompt_lower for word in ["contact", "reach", "support", "help"]):
        return "📞 **Contact Us:**\n- Website: datacrumbs.org\n- Email: help@datacrumbs.org\n- WhatsApp support available\n- Live chat on website\n- Social media: Follow us for updates and tips\n\nOur support team responds within 24 hours!"
    
    # Enrollment questions
    elif any(word in prompt_lower for word in ["how to start", "begin", "apply", "admission"]):
        return "🚀 **How to Get Started:**\n1. Choose your bootcamp based on career goals\n2. Fill out our enrollment form\n3. Schedule a consultation call\n4. Complete payment and secure your spot\n5. Receive course materials and start learning!\n\nReady to begin? I can show you our enrollment form!"
    
    # General greeting
    elif any(word in prompt_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return "👋 Hello! Welcome to Datacrumbs! I'm here to help you find the perfect bootcamp to advance your career in data science, analytics, or tech. What would you like to know about our courses?"
    
    # Default response
    else:
        return f"🤖 **I'm here to help with Datacrumbs!** I can provide information about:\n\n- Our 7 bootcamp programs\n- Course details, duration, and curriculum\n- Pricing and payment options\n- Prerequisites and requirements\n- Career support and job placement\n- Enrollment process\n\nWhat specific information can I help you with today?\n\n{datacrumbs_info}"

# Simple UI
st.title("🤖 Datacrumbs Chatbot")
st.subheader("Your AI assistant for course information and enrollment")

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
prompt = st.chat_input("Ask me about courses, pricing, enrollment, or anything else!")

if prompt:
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Better enrollment intent detection
    def wants_to_enroll(text):
        text_lower = text.lower()
        strong_intent = [
            "i want to enroll", "i want to register", "i want to sign up", "i want to join",
            "how do i enroll", "how do i register", "how can i join", "ready to enroll",
            "start enrollment", "begin enrollment", "fill enrollment", "enroll me",
            "register me", "sign me up", "i'm ready to start", "let's enroll"
        ]
        return any(phrase in text_lower for phrase in strong_intent)
    
    user_wants_to_enroll = wants_to_enroll(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        response_text = ""
        
        if llm:
            try:
                # Show thinking indicator
                with st.spinner("🤔 Thinking..."):
                    system_msg = SystemMessage(content=f"""
You are an expert virtual assistant for Datacrumbs education platform. Be helpful, friendly, and informative.

{datacrumbs_info}

Guidelines:
- Give detailed, helpful responses about courses and data science topics
- Be enthusiastic about learning and career growth
- If someone asks about enrollment/registration, mention you can help with the enrollment form
- Use emojis and formatting to make responses engaging
- Always provide actionable next steps
""")
                    
                    messages = [system_msg, HumanMessage(content=prompt)]
                    response = llm(messages)
                    response_text = response.content
                    
            except Exception as e:
                st.error(f"⚠️ AI response failed: {str(e)}")
                response_text = get_fallback_response(prompt)
        else:
            response_text = get_fallback_response(prompt)
        
        # Display response
        st.write(response_text)
        st.session_state.messages.append(AIMessage(content=response_text))
        
        # Show enrollment button for enrollment intent
        if user_wants_to_enroll:
            st.markdown("---")
            if st.button("📝 Open Enrollment Form", type="primary", use_container_width=True):
                st.session_state.show_enrollment = True
                st.rerun()

# Enrollment Form (rest of the form code remains the same)
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
        submitted = st.form_submit_button("🎯 Submit Enrollment & Pay Fee", type="primary")
        
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

# Sidebar with quick info
with st.sidebar:
    st.markdown("### 🚀 Quick Info")
    st.markdown("**Popular Courses:**")
    st.markdown("• Data Science Bootcamp")
    st.markdown("• Python Bootcamp") 
    st.markdown("• GenAI Bootcamp")
    st.markdown("• SQL Zero to Hero")
    
    st.markdown("---")
    st.markdown("**💬 Need Help?**")
    st.markdown("Email: help@datacrumbs.org")
    st.markdown("Website: datacrumbs.org")
