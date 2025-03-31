# DSA Tutor Pro

A comprehensive platform for learning Data Structures and Algorithms with AI-powered assistance.

## Features

- 📚 Curated DSA content and learning resources
- 💡 Interactive learning experience
- 📊 Progress tracking and analytics
- 🤖 AI-powered learning assistance
- ⚡ Real-time feedback
- 🎯 Targeted practice questions

## Tech Stack

- Frontend: Streamlit
- Backend: Flask
- Database: Supabase
- Authentication: Supabase Auth
- AI: DeepSeek API

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dsa-tutor-pro.git
cd dsa-tutor-pro
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=your_deepseek_api_url
ADMIN_SECRET=your_admin_secret
```

5. Run the application:
```bash
# Start the backend server
python run.py

# In a new terminal, start the frontend
streamlit run frontend/main.py
```

## Project Structure

```
dsa-tutor-pro/
├── app/
│   ├── __init__.py
│   ├── admin/
│   ├── users/
│   ├── progress/
│   ├── chatbot/
│   └── main/
├── frontend/
│   └── main.py
├── middlewares/
│   └── auth.py
├── config.py
├── requirements.txt
└── run.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
