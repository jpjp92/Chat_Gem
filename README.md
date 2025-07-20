# 🤖 Chat with Gemini

<div align="center">
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/Chat_Gem.svg)](https://github.com/yourusername/Chat_Gem/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/yourusername/Chat_Gem.svg)](https://github.com/yourusername/Chat_Gem/pulls)
</div>

## ✨ Overview

Chat with Gemini is a powerful AI chat application built with Streamlit and the Google Gemini API. It supports webpage summarization, YouTube video summarization, PDF document summarization, image analysis, and natural conversation in both Korean and English. With a user-friendly interface and robust session management, it offers an intuitive and seamless AI interaction experience.

## 🚀 Features

### 🌐 Webpage Summarization
Input a URL to receive a concise summary of the webpage content.

### 📺 YouTube Video Summarization
Provide a YouTube link to get a summary based on the video's transcript.

### 📄 PDF Document Summarization
Submit a PDF URL (e.g., arXiv) to obtain a summary of the document.

### 🖼️ Image Analysis
Upload images and ask questions or request analysis.

### 💬 Natural Conversation
Engage in free-form conversation with Gemini AI in Korean or English.

### 🔒 Session Management
Create, save, delete, and export/import multiple chat sessions in JSON format, with usage tracking.

### 🌍 Multilingual Support
Automatically detects Korean or English input for seamless language switching.

### 📊 Usage Tracking
Displays daily usage with a visual progress bar to manage limits.

## 🛠️ Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (generated via Google Cloud Console)
- Streamlit and other Python dependencies (see installation below)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Chat_Gem.git
cd Chat_Gem
```

### 2. Install Dependencies

Install the required Python packages. If a requirements.txt file is not provided, use the following command to install the core dependencies:

```bash
pip install streamlit google-generativeai pillow python-dotenv requests
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root directory.

Add your Google Gemini API key as follows:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note:** Obtain your API key from the Google Cloud Console.

Alternatively, configure the API key using Streamlit Secrets by adding the following to `secrets.toml`:

```toml
[secrets]
GEMINI_API_KEY = "your_gemini_api_key_here"
```

### 4. Run the Application

Launch the Streamlit application with the following command:

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501` to access the application.

## 📂 Project Structure

```
Chat_Gem/
├── app.py               # Main application file
├── config/
│   ├── env.py          # Environment variable configuration
│   ├── imports.py      # Library imports
│   ├── prompts.py      # Gemini prompts and functions
│   ├── style.py        # Custom CSS styles
│   ├── utils.py        # Utility functions
├── .env                # Environment variables (e.g., API key)
├── README.md           # Project documentation
```

## 🖥️ Usage

### Start a Chat
Click the "New Chat" button in the sidebar to begin a new session.
Enter your query in the text input field or upload images to start a conversation.

### Using Features

- **Webpage Summarization**: Enter a URL and request, e.g., "Summarize this website."
- **YouTube Summarization**: Provide a YouTube URL and ask, e.g., "Summarize this video."
- **PDF Summarization**: Input a PDF URL and request, e.g., "Summarize this PDF."
- **Image Analysis**: Upload images and ask, e.g., "Analyze this image."
- **General Conversation**: Ask any question or engage in casual conversation.

### Session Management
View, load, or delete previous chat sessions from the sidebar.
Export conversations as JSON files or start a new session.

### Language Settings
Select Korean or English from the sidebar to change the system language.
The app automatically detects the input language for appropriate responses.

### Usage Monitoring
Check daily usage in the sidebar, with warnings for nearing or exceeding limits.

## 💡 Tips

- **Specific Queries**: Provide detailed questions for more accurate responses.
- **Session Persistence**: Sessions are automatically saved, allowing you to revisit past conversations.
- **Image Uploads**: Supported formats are PNG, JPEG, and WebP (up to 7MB).
- **Multilingual Support**: Mix Korean and English freely; the app adapts automatically.

## ⚠️ Notes

- **API Key Security**: Store your API key securely in `.env` or Streamlit Secrets.
- **Usage Limits**: The free version has a daily limit of 100 interactions, trackable in the sidebar.
- **Supported Image Formats**: PNG, JPEG, WebP (max 7MB).
- **Error Handling**: User-friendly error messages are displayed for invalid API keys or requests.

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

- Create an issue to report bugs or suggest features.
- Fork the repository, make changes, and submit a pull request.
- Participate in code reviews or improve documentation.

## 📜 License

This project is licensed under the MIT License.

## 📞 Contact

For inquiries, reach out via:

- **GitHub**: jpjp92
- **Email**: johnnyworld9278@gmail.com