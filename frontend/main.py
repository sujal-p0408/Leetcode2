import streamlit as st
import requests
import json
from PIL import Image
import os
from dotenv import load_dotenv
from supabase import create_client

# Configure page with dark theme and wide layout
st.set_page_config(
    page_title="DSA Tutor Pro",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Backend URL
BACKEND_URL = "http://127.0.0.1:5000"

# API endpoints
API_ENDPOINTS = {
    "signup": f"{BACKEND_URL}/api/signup",
    "login": f"{BACKEND_URL}/api/login",
    "articles": f"{BACKEND_URL}/api/articles",
    "progress": f"{BACKEND_URL}/api/user/progress",
    "chat": f"{BACKEND_URL}/api/chat/api/chat",
    "ai_assist": f"{BACKEND_URL}/api/ai/assist"
}

# Get environment variables and create Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Add this after creating the supabase client
try:
    # Test backend connection
    response = requests.get(f"{BACKEND_URL}/health")
    if response.status_code == 200:
        print("Connected to backend successfully")
    else:
        print("Backend connection failed:", response.text)
except Exception as e:
    print("Backend connection error:", str(e))

def get_working_api_url():
    possible_urls = [
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ]
    
    st.write("🔍 Checking available backend servers...")
    
    for url in possible_urls:
        try:
            st.write(f"Trying to connect to: {url}")
            response = requests.get(f"{url}/", timeout=2)
            if response.status_code == 200:
                st.success(f"✅ Found working backend at: {url}")
                return url
        except requests.exceptions.ConnectionError:
            st.warning(f"❌ Could not connect to: {url}")
        except Exception as e:
            st.warning(f"❌ Error connecting to {url}: {str(e)}")
    
    st.error("❌ No working backend server found!")
    st.info("""
    To fix this:
    1. Make sure the backend server is running
    2. Open a new terminal
    3. Navigate to the project root directory
    4. Start the Flask server:
       ```
       python run.py
       ```
    5. You should see: "Running on http://127.0.0.1:5000"
    """)
    
    # Default fallback
    return "http://127.0.0.1:5000"

API_BASE_URL = get_working_api_url()  # Dynamically find working URL

def init_session_state():
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'completed_questions' not in st.session_state:
        st.session_state.completed_questions = set()

def signup():
    st.subheader("Sign Up")
    
    # Create a container for success messages
    success_container = st.container()
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        username = st.text_input("Username")
        phone = st.text_input("Phone")
        admin_code = st.text_input("Admin Code (Optional)", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not email or not password or not username or not phone:
                st.error("All fields are required except Admin Code")
                return

            data = {
                "email": email,
                "password": password,
                "username": username,
                "phone": phone
            }
            if admin_code:
                data["admin_code"] = admin_code

            try:
                response = requests.post(
                    API_ENDPOINTS["signup"],
                    headers={"Content-Type": "application/json"},
                    json=data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    with success_container:
                        if response_data.get("status") == "resent":
                            st.success("""
                            ✅ Verification email resent! 
                            
                            Please check your email for verification:
                            1. Look in your inbox for an email from Supabase
                            2. Check your spam folder if you don't see it
                            3. Click the verification link in the email
                            4. After verification, you can log in
                            
                            If you still don't receive the email, please try:
                            1. Using a different email address
                            2. Checking your spam folder
                            3. Waiting a few minutes and trying again
                            """)
                        else:
                            st.success("""
                            ✅ Signup successful! 
                            
                            Please check your email for verification:
                            1. Look in your inbox for an email from Supabase
                            2. Check your spam folder if you don't see it
                            3. Click the verification link in the email
                            4. After verification, you can log in
                            
                            If you don't receive the email within a few minutes, please try signing up again.
                            """)
                        
                        # Add a resend verification button outside the form
                        if st.button("Resend Verification Email"):
                            try:
                                resend_response = requests.post(
                                    f"{API_BASE_URL}/resend-verification",
                                    headers={"Content-Type": "application/json"},
                                    json={"email": email}
                                )
                                if resend_response.status_code == 200:
                                    st.success("Verification email resent! Please check your inbox.")
                                else:
                                    st.error("Failed to resend verification email. Please try again.")
                            except Exception as e:
                                st.error(f"Error resending verification email: {str(e)}")
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error occurred")
                        if "already registered" in error_msg.lower():
                            st.error("""
                            This email is already registered. 
                            
                            If you haven't received the verification email:
                            1. Check your spam folder
                            2. Try using the 'Resend Verification Email' button below
                            3. Or try using a different email address
                            """)
                        else:
                            st.error(f"Signup failed: {error_msg}")
                    except ValueError:
                        st.error(f"Signup failed: {response.text}")
                        
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Unable to connect to server. Please check your internet connection.")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Network error: {str(e)}")

def login():
    st.subheader("Login")
    
    # Show the current API URL being used
    st.info(f"API URL: {API_BASE_URL}")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return
                
            try:
                response = requests.post(
                    API_ENDPOINTS["login"],
                    headers={"Content-Type": "application/json"},
                    json={"email": email, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data.get("token", "default_token")
                    st.session_state.user_role = data.get("role", "user")
                    st.success("✅ Login successful!")
                    st.rerun()
                elif response.status_code == 401:
                    st.error("❌ Invalid credentials. Please check your email and password.")
                    # Show test credentials as a hint
                    st.code("Email: test@example.com\nPassword: password123")
                else:
                    st.error(f"❌ Login failed with status code: {response.status_code}")
                    if hasattr(response, 'text'):
                        st.error(f"Response: {response.text}")
                
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Connection error. Backend server is not running.")
                st.info("To fix this:")
                st.code("""
                # 1. Open a new terminal
                # 2. Navigate to your project root directory
                cd .
                
                # 3. Start the Flask server
                python run.py
                
                # 4. You should see: "Running on http://127.0.0.1:5000"
                """)
            except requests.exceptions.Timeout:
                st.error("⚠️ Request timed out. The server took too long to respond.")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.info("Please check if the backend server is running properly.")

def display_articles():
    st.header("Learning Resources")
    
    if 'token' not in st.session_state or not st.session_state.token:
        st.error("Please login first")
        return
    
    # Show the current API URL being used
    st.info(f"API URL: {API_BASE_URL}")
    
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }
    
    try:
        # First, check if the server is running with a health check
        try:
            health_check_url = f"{API_BASE_URL}/"
            st.write(f"Checking server health at: {health_check_url}")
            health_response = requests.get(health_check_url, timeout=5)
            st.success(f"✅ Server is running. Status: {health_response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
            st.code("""
            # Run this command in a new terminal:
            cd app/backend
            python app.py
            """)
            return
        except Exception as e:
            st.error(f"❌ Server health check error: {str(e)}")
            return
        
        # Now fetch the articles
        url = API_ENDPOINTS["articles"]
        st.write(f"Fetching articles from: {url}")
        
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        
        st.write(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                articles = response.json()
                st.success(f"✅ Successfully retrieved {len(articles)} articles")
                
                if not articles:
                    st.info("No articles available yet.")
                else:
                    # Initialize completed articles in session state if not exists
                    if 'completed_articles' not in st.session_state:
                        st.session_state.completed_articles = set()
                    
                    for article in articles:
                        article_id = article.get('id')
                        with st.expander(f"📚 {article.get('title', 'Untitled')}"):
                            st.markdown(article.get('content', 'No content available'))
                            
                            # Add checkbox for article completion
                            is_completed = article_id in st.session_state.completed_articles
                            if st.checkbox("Mark as Completed", key=f"article_{article_id}", value=is_completed):
                                try:
                                    # Call backend to mark article as completed
                                    mark_response = requests.post(
                                        f"{API_BASE_URL}/api/articles/{article_id}/mark-read",
                                        headers=headers,
                                        timeout=5
                                    )
                                    
                                    if mark_response.status_code == 200:
                                        st.session_state.completed_articles.add(article_id)
                                        st.success("✅ Article marked as completed!")
                                    else:
                                        st.error("Failed to mark article as completed")
                                except Exception as e:
                                    st.error(f"Error marking article as completed: {str(e)}")
            except ValueError:
                st.error("Invalid response format from server")
                st.write("Response content:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
        elif response.status_code == 401:
            st.error("Session expired or invalid token. Please login again.")
            st.session_state.token = None
            st.rerun()
        else:
            st.error(f"Error fetching articles. Status code: {response.status_code}")
            st.write("Response content:", response.text)
            
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. The server took too long to respond.")
        st.info("This usually indicates the server is overloaded or not responding properly.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to the server.")
        st.info("""
        Please check:
        1. The backend server is running
        2. There are no firewall/network issues
        3. The API URL is correct
        """)
        st.code("""
        # Start the backend server:
        cd app/backend
        python app.py
        """)
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
        st.info("Please check if the backend server is running properly.")

def display_progress():
    st.header("Learning Analytics")
    
    if 'token' not in st.session_state or not st.session_state.token:
        st.error("Please login first")
        return
    
    # Show the current API URL being used
    st.info(f"API URL: {API_BASE_URL}")
    
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }
    
    try:
        # First, check if the server is running with a health check
        try:
            health_check_url = f"{API_BASE_URL}/"
            st.write(f"Checking server health at: {health_check_url}")
            health_response = requests.get(health_check_url, timeout=5)
            st.success(f"✅ Server is running. Status: {health_response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
            st.code("""
            # Run this command in a new terminal:
            cd app/backend
            python app.py
            """)
            return
        except Exception as e:
            st.error(f"❌ Server health check error: {str(e)}")
            return
        
        # Now fetch the progress data
        url = API_ENDPOINTS["progress"]
        st.write(f"Fetching progress data from: {url}")
        
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        
        st.write(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Display overall progress
                st.subheader("Overall Progress")
                progress = data.get("progress", {})
                total_articles = progress.get("total_articles", 0)
                completed_articles = progress.get("completed_articles", 0)
                progress_percentage = progress.get("progress_percentage", 0)
                
                # Create columns for metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Articles", total_articles)
                with col2:
                    st.metric("Completed Articles", completed_articles)
                with col3:
                    st.metric("Progress", f"{progress_percentage:.1f}%")
                
                # Progress bar
                st.progress(progress_percentage / 100)
                
                # Display detailed progress data
                st.subheader("Completed Articles")
                progress_data = data.get("progress_data", [])
                if progress_data:
                    for item in progress_data:
                        with st.expander(f"Article ID: {item.get('article_id', 'N/A')}"):
                            st.write(f"Completed at: {item.get('completed_at', 'N/A')}")
                            
                            # Fetch article details
                            try:
                                article_response = requests.get(
                                    f"{API_BASE_URL}/api/articles/{item.get('article_id')}",
                                    headers=headers,
                                    timeout=5
                                )
                                if article_response.status_code == 200:
                                    article = article_response.json()
                                    st.write(f"Title: {article.get('title', 'N/A')}")
                                    st.write(f"Category: {article.get('category', 'N/A')}")
                            except Exception as e:
                                st.error(f"Error fetching article details: {str(e)}")
                else:
                    st.info("No articles completed yet. Start learning to track your progress!")
                
            except ValueError:
                st.error("Invalid response format from server")
                st.write("Response content:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
        elif response.status_code == 401:
            st.error("Session expired or invalid token. Please login again.")
            st.session_state.token = None
            st.rerun()
        else:
            st.error(f"Error fetching progress data. Status code: {response.status_code}")
            st.write("Response content:", response.text)
            
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. The server took too long to respond.")
        st.info("This usually indicates the server is overloaded or not responding properly.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to the server.")
        st.info("""
        Please check:
        1. The backend server is running
        2. There are no firewall/network issues
        3. The API URL is correct
        """)
        st.code("""
        # Start the backend server:
        cd app/backend
        python app.py
        """)
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
        st.info("Please check if the backend server is running properly.")

def display_ai_assistance():
    st.header("🤖 AI Learning Assistant")
    
    if 'token' not in st.session_state or not st.session_state.token:
        st.error("Please login first")
        return
        
    with st.expander("Get Personalized Help"):
        user_question = st.text_area("Ask your DSA question:")
        if st.button("Get AI Help"):
            with st.spinner("Thinking..."):
                try:
                    # Show the API endpoint being used
                    st.info(f"Using endpoint: {API_ENDPOINTS['ai_assist']}")
                    
                    # Increase timeout to 60 seconds
                    response = requests.post(
                        API_ENDPOINTS["ai_assist"],
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        },
                        json={"question": user_question},
                        timeout=60  # Increased timeout
                    )
                    
                    # Debug information
                    st.write(f"Response status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            ai_response = response.json()
                            st.markdown("### 💡 AI Response")
                            st.markdown(ai_response.get('response', ''))
                            
                            if ai_response.get('code_example'):
                                st.markdown("### 📝 Code Example")
                                st.code(ai_response['code_example'], language='python')
                        except json.JSONDecodeError:
                            st.error("Invalid response format from server")
                            st.write("Raw response:", response.text)
                    else:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", "Failed to get AI response")
                            st.error(f"Error: {error_msg}")
                        except json.JSONDecodeError:
                            st.error(f"Error: {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("""
                    Request timed out. This might be because:
                    1. The AI model is taking longer than expected to respond
                    2. The server is experiencing high load
                    
                    Please try again in a few moments. If the problem persists:
                    1. Try asking a shorter question
                    2. Check your internet connection
                    3. Contact support if the issue continues
                    """)
                except requests.exceptions.ConnectionError:
                    st.error("""
                    Cannot connect to server. Please check:
                    1. The backend server is running
                    2. Your internet connection is working
                    3. There are no firewall issues
                    
                    To start the backend server:
                    ```bash
                    python run.py
                    ```
                    """)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.write("Full error details:", str(e))

def ai_chatbot():
    st.header("🤖 AI DSA Tutor")
    
    if 'token' not in st.session_state or not st.session_state.token:
        st.error("Please login first")
        return
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about Data Structures and Algorithms..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Show thinking message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call backend API
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat",
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        },
                        json={"prompt": prompt},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        ai_response = response.json()["response"]
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        st.markdown(ai_response)
                    else:
                        error_msg = response.json().get("error", "Failed to get response")
                        st.error(f"Error: {error_msg}")
                        
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to server. Please check if the backend is running.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    
    # Add a clear chat button in the sidebar
    with st.sidebar:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

def main():
    # Initialize session state
    init_session_state()
    
    # Custom CSS for a more technical look
    st.markdown("""
        <style>
        .main {
            background-color: #0E1117;
        }
        .stButton button {
            background-color: #3B71CA;
            color: white;
            border-radius: 5px;
            transition: transform 0.2s ease, background-color 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            background-color: #2C5282;
        }
        
        /* Animated logo */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 0rem;
            padding: 1rem 0;
            margin-bottom: 0;
            animation: fadeIn 0.8s ease-out;
        }
        
        .logo-icon {
            font-size: 4.5rem;
            margin-right: -0.8rem;
            margin-left: -0.5rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .logo-text {
            font-weight: 900;
            color: #FFFFFF;
            font-size: 3rem;
            margin-bottom: 1rem;
            letter-spacing: -1px;
            margin-left: 0.7rem;
            animation: fadeIn 0.8s ease-out;
        }
        
        /* Animated cards */
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .stExpander {
            border: 1px solid #2E3440;
            border-radius: 8px;
            margin-bottom: 10px;
            animation: slideIn 0.5s ease-out;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stExpander:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Progress bar animation */
        @keyframes progressFill {
            from { width: 0; }
            to { width: 100%; }
        }
        
        /* Success message animation */
        @keyframes pulseSuccess {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .success {
            padding: 1rem;
            border-radius: 5px;
            background-color: #1E2749;
            animation: pulseSuccess 2s infinite;
        }
        
        /* Metric animations */
        .stMetric {
            transition: transform 0.3s ease;
        }
        
        .stMetric:hover {
            transform: scale(1.05);
        }
        
        /* Tab animations */
        .stTabs {
            transition: opacity 0.3s ease;
        }
        
        .stTab {
            transition: all 0.3s ease;
        }
        
        .stTab:hover {
            transform: translateY(-2px);
        }
        
        /* Search bar animation */
        .stTextInput input {
            border: 1px solid #3B71CA;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            transform: scale(1.01);
            box-shadow: 0 0 15px rgba(59, 113, 202, 0.2);
        }
        
        /* Category tag animation */
        .category-tag {
            background-color: #1E2749;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            color: #3B71CA;
            transition: all 0.3s ease;
        }
        
        .category-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Logo subtitle animation */
        .logo-subtitle {
            color: #6C757D;
            font-size: 1rem;
            margin-top: -1rem;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-out 0.3s backwards;
        }
        
        /* Sidebar logo */
        .sidebar-logo {
            font-size: 3rem;
            margin-right: 0rem;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 2rem;
            margin-bottom: 2rem;
            width: 100%;
        }
        
        .title-section {
            flex: 0 0 auto;
            margin-right: auto;
        }
        
        .quote-container {
            flex: 0 0 50%;
            background: linear-gradient(135deg, rgba(30, 39, 73, 0.6), rgba(44, 62, 80, 0.6));
            border: 1px solid rgba(59, 113, 202, 0.3);
            border-radius: 15px;
            padding: 15px 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(59, 113, 202, 0.1);
            animation: glow 3s infinite alternate;
            margin-top: 10px;
            margin-right: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.token is None:
        # Logo and Title for login page
        col1, col2 = st.columns([0.25, 5])
        with col1:
            st.markdown('<div class="logo-icon">👽</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="logo-text">DSA Tutor Pro</div>', unsafe_allow_html=True)
            st.markdown('<div class="logo-subtitle">Master Data Structures & Algorithms</div>', unsafe_allow_html=True)

        # Login page content
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.container():
                st.markdown("""
                    ### 🚀 Welcome to DSA Tutor Pro
                    Your personal guide to mastering algorithms
                    
                    - 📚 Curated DSA content
                    - 💡 Interactive learning
                    - 📊 Progress tracking
                    - 🤖 AI-powered assistance
                    - ⚡ Real-time feedback
                    - 🎯 Targeted practice
                """)
        with col2:
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            with tab1:
                login()
            with tab2:
                signup()
    else:
        # Combined header with logo and quote
        st.markdown("""
            <div class="header-container">
                <div class="title-section">
                    <div class="logo-container">
                        <div class="logo-icon">👽</div>
                        <div>
                            <div class="logo-text">DSA Tutor Pro</div>
                            <div class="logo-subtitle">Master Data Structures & Algorithms</div>
                        </div>
                    </div>
                </div>
                <div class="quote-container">
                    <div class="quote-header">
                        <span class="tech-icon">⚡</span>Code of the Day
                    </div>
                    <div class="quote-text">
                        "First, solve the problem. Then, write the code."
                    </div>
                    <div class="quote-author">
                        - John Johnson
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Sidebar with user info and stats
        with st.sidebar:
            st.markdown("""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <div class="logo-text" style='font-size: 2rem;'><span class="sidebar-logo">👽</span> DSA Pro</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 👤 User Dashboard")
            st.success("🟢 Logged in successfully!")
            
            # Add quick stats in sidebar
            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Questions", len(st.session_state.completed_questions))
            with col2:
                progress_percent = len(st.session_state.completed_questions) * 100 / 50  # Assuming 50 total questions
                st.metric("Progress", f"{progress_percent:.1f}%")
            
            if st.button("🚪 Logout", type="primary"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

        # Main content area
        tab1, tab2, tab3 = st.tabs(["📚 Learning Hub", "📈 Progress Analytics", "🤖 AI Assistant"])
        with tab1:
            display_articles()
        with tab2:
            display_progress()
        with tab3:
            display_ai_assistance()

if __name__ == "__main__":
    main()