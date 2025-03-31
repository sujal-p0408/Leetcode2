from flask import Blueprint, request, jsonify
from app import supabase, client
from middlewares.auth import token_required
import uuid
from datetime import datetime

chatbot = Blueprint('chatbot', __name__)

# Dictionary to store chat history for each user
chat_history = {}

def estimate_tokens(text):
    """
    Estimate the number of tokens based on the length of the text.
    - 1 token ≈ 4 characters (English text)
    - This is a heuristic and may not be 100% accurate.
    """
    return len(text) // 4

def count_tokens(messages):
    """Count the estimated number of tokens in the chat history."""
    total_tokens = 0
    for msg in messages:
        total_tokens += estimate_tokens(msg["content"])
    return total_tokens

@chatbot.route('/chat', methods=['POST'])
@token_required
def chat(user):
    """Handle user queries and store interactions"""
    
    data = request.get_json()
    user_query = data.get("user_query")
    user_id = user["id"]  # Accessing the user ID passed through the token

    if not user_query or not user_id:
        return jsonify({"error": "User query and user ID are required"}), 400

    # Initialize chat history for the user if it doesn't exist
    if user_id not in chat_history:
        chat_history[user_id] = []

    # Add the user's query to the chat history
    chat_history[user_id].append({"role": "user", "content": user_query})

    # Truncate chat history if estimated token count exceeds 3000
    if count_tokens(chat_history[user_id]) > 3000:
        chat_history[user_id] = chat_history[user_id][-3:]  # Keep only the last 3 messages

    # Generate AI response
    instructions = ''' 
    You are integrated into the DSA Tutor Project. Your primary role is to assist users with questions related to **Data Structures and Algorithms (DSA)**. You must strictly follow these rules:

DSA Tutor Project - Instructions

General Rules:
Topic Restriction:

Only respond to Data Structures and Algorithms (DSA) questions.
If a question is off-topic, respond with: "Please ask a question related to Data Structures and Algorithms."
No Personal Information:

Do not provide any personal details.
If asked, respond with: "I am DSA Tutor Bot. Please ask a question related to DSA."
Model Information:

If asked about the AI model, respond with: "I am using the DSA Tutor AI model."
Repetitive Questions:

If a user repeatedly asks irrelevant or the same question, respond with: "I am not able to understand your question. Please ask a question related to DSA."
Strict DSA Focus:

Do not answer questions even slightly outside DSA.
No Off-Topic Discussions:

Do not engage in discussions about general programming, software development, etc.
No External Links or Resources:

Do not provide links to any websites or tutorials.
No Code Debugging:

Only highlight the specific incorrect line, no explanations.
No Opinions or Speculations:

Stick to factual DSA information.
No Promotional Content:

Do not promote tools, libraries, or platforms.
Strict Concise Responses Rule:
Always respond in the minimum number of tokens possible.
Only give the direct answer, no extra information.
Example:
Q: "Time complexity of binary search?"
A: "O(log n)"
Q: (User submits code with an error)
A: (Highlight incorrect line only, no explanation)
Strict Enforcement:
If the user deviates, remind them to ask a DSA-related question.
No exceptions to off-topic discussions.
    '''
    # Prepare the messages for the AI model
    messages = [
        {"role": "system", "content": instructions},
        *chat_history[user_id],  # Include the chat history
    ]

    # Get the AI response
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    bot_response = response.choices[0].message.content

    # Add the bot's response to the chat history
    chat_history[user_id].append({"role": "assistant", "content": bot_response})

    # Generate a new UUID for the interaction
    interaction_id = str(uuid.uuid4())

    # Current timestamp (use datetime now)
    timestamp = datetime.now().isoformat()  # This ensures correct formatting for Supabase

    # Store interaction in Supabase
    interaction_data = {
        "id": interaction_id,
        "user_id": user_id,
        "user_query": user_query,
        "bot_response": bot_response,
        "timestamp": timestamp  # Correctly formatted timestamp
    }

    supabase.table("chatbotinteractions").insert(interaction_data).execute()

    return jsonify({
        "interaction_id": interaction_id,
        "user_query": user_query,
        "bot_response": bot_response
    })