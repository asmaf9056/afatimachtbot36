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
            model="gemini-1.5-flash",  # Faster model
            google_api_key=api_key,
            temperature=0.3,  # Lower temperature for faster, more consistent responses
            timeout=5,  # Reduced timeout
            max_tokens=300  # Limit response length for speed
        )
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
    
    # Fast keyword matching with shorter, more targeted responses
    
    # General information/details questions
    if any(word in prompt_lower for word in ["info", "information", "details", "tell me about", "what is", "explain", "describe"]):
        return "📋 **Datacrumbs Overview:**\n\n🎯 **7 Tech Bootcamps Available:**\n• Data Science • Analytics • Business Intelligence\n• GenAI • Python • SQL • Excel\n\n✨ **Key Features:** Industry curriculum, real projects, certificates, job support, flexible schedule\n\n💬 Ask about: pricing, duration, enrollment, or specific courses!"
    
    # Pricing questions
    elif any(word in prompt_lower for word in ["price", "cost", "fee", "payment", "money", "expensive", "cheap", "affordable"]):
        return "💰 **Quick Pricing Info:**\n✅ Competitive rates with payment plans\n✅ Student & early bird discounts\n✅ Scholarship opportunities\n\n📧 **Get Exact Pricing:** help@datacrumbs.org\n🚀 **Ready to enroll?** I can show you the form!"
    
    # Duration and timing questions
    elif any(word in prompt_lower for word in ["duration", "time", "long", "weeks", "months", "timings", "schedule", "when", "directions", "time of day", "timestamp", "hours"]):
        return "⏰ **Course Duration:**\n• Data Science: 12-16 weeks\n• Analytics: 8-12 weeks\n• Python: 8-10 weeks\n• GenAI: 6-8 weeks\n• SQL: 4-6 weeks\n• Excel: 3-4 weeks\n\n🕐 **Flexible Schedule:** Weekend & evening batches available!"
    
    # Prerequisites questions
    elif any(word in prompt_lower for word in ["prerequisite", "requirement", "beginner", "experience", "qualification", "background"]):
        return "✅ **Prerequisites:**\n🟢 **Beginner-Friendly:** Excel, SQL, Python, GenAI\n🟡 **Basic Skills Helpful:** Data Science, Analytics\n\n🎯 **Bottom Line:** We teach from scratch! All backgrounds welcome."
    
    # Certificate questions
    elif any(word in prompt_lower for word in ["certificate", "certification", "credential", "diploma", "degree"]):
        return "🏆 **Industry Certificates:**\n✅ Verified & employer-recognized\n✅ Includes project portfolio\n✅ Boosts resume & LinkedIn\n\n🎯 **Awarded upon completion** of any bootcamp!"
    
    # Job/career questions
    elif any(word in prompt_lower for word in ["job", "career", "placement", "employment", "salary", "hiring", "work", "opportunity"]):
        return "💼 **Career Support:**\n✅ Resume building & interview prep\n✅ Job placement with partners\n✅ LinkedIn optimization\n✅ Portfolio development\n\n📈 **Success Rate:** Most graduates get jobs within 3-6 months!"
    
    # Contact questions
    elif any(word in prompt_lower for word in ["contact", "reach", "support", "help", "phone", "email", "whatsapp"]):
        return "📞 **Contact Info:**\n🌐 Website: datacrumbs.org\n📧 Email: help@datacrumbs.org\n💬 WhatsApp support available\n\n⚡ **Response Time:** Within 24 hours!"
    
    # Location and directions
    elif any(word in prompt_lower for word in ["location", "address", "where", "directions", "map", "office"]):
        return "📍 **Learning Options:**\n🖥️ **Online:** Live sessions + recordings\n🏢 **Offline:** Contact for locations\n\n📧 **Directions:** help@datacrumbs.org\n💬 **WhatsApp:** Available for quick help!"
    
    # Enrollment questions
    elif any(word in prompt_lower for word in ["how to start", "begin", "apply", "admission", "enroll", "register", "sign up", "join"]):
        return "🚀 **Quick Start Process:**\n1️⃣ Choose your course\n2️⃣ Fill enrollment form\n3️⃣ Schedule consultation\n4️⃣ Make payment\n5️⃣ Start learning!\n\n🎯 **Ready?** I can open the enrollment form now!"
    
    # General greeting
    elif any(word in prompt_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return "👋 **Welcome to Datacrumbs!** \n\nI'm your AI assistant for tech bootcamps! \n\n🎯 **Quick Help:** Ask about courses, pricing, enrollment, or schedules\n💡 **Popular:** Data Science, Python, GenAI bootcamps"
    
    # Default response
    else:
        return "🤖 **I can help with:**\n\n🎓 **7 Bootcamps:** Data Science, Analytics, BI, GenAI, Python, SQL, Excel\n💰 **Pricing & Payment Plans**\n⏰ **Duration & Schedules**\n🚀 **Enrollment Process**\n💼 **Career Support**\n\n❓ **What would you like to know?**"

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
                    system_msg = SystemMessage(content=f"""You are a friendly Datacrumbs assistant. Keep responses under 200 words, use emojis, be enthusiastic about tech education.

COURSES: Data Science, Analytics, BI, GenAI, Python, SQL, Excel bootcamps
FEATURES: Industry curriculum, real projects, certificates, job support
CONTACT: help@datacrumbs.org, datacrumbs.org

Be concise and actionable.""")
                    
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
