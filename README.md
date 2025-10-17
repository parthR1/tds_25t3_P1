# TDS Project 1 - Automated Code Deployment System

An automated system that uses LLMs to build, deploy, and update web applications based on task briefs. Built for the Tools in Data Science course at IIT Madras.

## 🎯 What This Does

This application:

1. **Receives** task requests via a REST API
2. **Generates** complete web applications using AIPipe/Claude LLM
3. **Creates** GitHub repositories automatically
4. **Deploys** to GitHub Pages
5. **Updates** applications for Round 2 revisions
6. **Submits** evaluation data back to the instructor's API

## 🏗️ Architecture

```
Task Request → FastAPI Endpoint → LLM Generation → Git Repo Creation → GitHub Pages → Evaluation Submission
```

### Key Components

- **`main.py`**: FastAPI server handling task requests and orchestrating the workflow
- **`llm_generator.py`**: LLM integration using AIPipe for code generation
- **Environment Variables**: Secure credential management

## 📋 Features

✅ Automated GitHub repository creation  
✅ LLM-powered code generation (using AIPipe)  
✅ GitHub Pages deployment  
✅ Round 2 revision support  
✅ Attachment handling (CSV, Markdown, JSON)  
✅ Retry logic for API submissions  
✅ Comprehensive logging  
✅ Error handling and recovery

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Git installed and configured
- GitHub account with Personal Access Token
- AIPipe API key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/tds_25t3_P1.git
cd tds_25t3_P1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=ghp_your_token_here
AIPIPE_API_KEY=your_aipipe_key_here
SECRET=ljao(23$*dfs#1023-49($HC9203*&(23
```

**Get your tokens:**

- GitHub: https://github.com/settings/tokens (needs `repo` scope)
- AIPipe: https://aipipe.org/

### 4. Run

```bash
python main.py
```

Server starts on `http://localhost:8000`

### 5. Test

```bash
curl -X POST http://localhost:8000/initiate_task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "ljao(23$*dfs#1023-49($HC9203*&(23",
    "task": "test-task-001",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a Bootstrap page with heading and button",
    "checks": ["Has Bootstrap CSS", "Has h1 element", "Has button"],
    "evaluation_url": "https://webhook.site/your-id",
    "attachments": []
  }'
```

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)**: Detailed setup instructions
- **[API Documentation](#api-endpoints)**: Endpoint reference
- **[Deployment Guide](SETUP_GUIDE.md#deployment-options)**: How to deploy to production

## 🔌 API Endpoints

### `POST /initiate_task`

Receives a task request and processes it.

**Request Body:**

```json
{
  "email": "student@example.com",
  "secret": "your_secret",
  "task": "task-id",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Task description",
  "checks": ["Check 1", "Check 2"],
  "evaluation_url": "https://api.example.com/evaluate",
  "attachments": [
    {
      "name": "data.csv",
      "url": "data:text/csv;base64,..."
    }
  ]
}
```

**Response:**

```json
{
  "message": "Task received and processing started"
}
```

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "github_token": "configured",
  "aipipe_token": "configured"
}
```

## 🔄 How It Works

### Round 1: Build & Deploy

1. Receive task request
2. Validate secret
3. Generate application code using LLM
4. Create GitHub repository
5. Push code to repository
6. Enable GitHub Pages
7. Submit evaluation data

### Round 2: Revise & Update

1. Receive revision request
2. Clone existing repository
3. Generate updated code using LLM
4. Commit and push changes
5. Submit updated evaluation data

## 🛠️ Technology Stack

- **FastAPI**: Web framework
- **AIPipe**: LLM API access (Claude)
- **GitHub API**: Repository management
- **Git**: Version control
- **Python**: Core language

## 📊 Project Structure

```
tds_25t3_P1/
├── main.py              # FastAPI server & orchestration
├── llm_generator.py     # LLM code generation logic
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── SETUP_GUIDE.md      # Detailed setup instructions
└── test_requests.sh    # Test script
```

## 🧪 Testing

### Local Testing

```bash
# Start server
python main.py

# Run test script
chmod +x test_requests.sh
./test_requests.sh local
```

### Production Testing

```bash
./test_requests.sh production
```

## 🚢 Deployment

### Option 1: Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Connect GitHub repository
2. Add environment variables
3. Deploy

### Option 2: Render

1. Create Web Service
2. Connect repository
3. Set environment variables
4. Deploy

See [SETUP_GUIDE.md](SETUP_GUIDE.md#deployment-options) for detailed instructions.

## 🐛 Troubleshooting

### Common Issues

**Issue**: "GITHUB_TOKEN not set"

- Ensure `.env` file exists with correct token

**Issue**: "Repository creation failed"

- Check GitHub token has `repo` scope
- Verify token hasn't expired

**Issue**: "LLM generation fails"

- Verify AIPipe API key is valid
- Check AIPipe credit balance

See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for more solutions.

## 📝 Example Tasks

### Task 1: CSV Data Summary

```json
{
  "brief": "Create a page that sums the sales column from data.csv",
  "checks": ["Loads Papaparse library", "Element #total-sales shows sum"],
  "attachments": [{ "name": "data.csv", "url": "data:text/csv;base64,..." }]
}
```

### Task 2: Markdown Renderer

```json
{
  "brief": "Convert markdown to HTML using marked library",
  "checks": ["Loads marked.js", "Element #output contains rendered HTML"],
  "attachments": [
    { "name": "input.md", "url": "data:text/markdown;base64,..." }
  ]
}
```

### Task 3: GitHub User Lookup

```json
{
  "brief": "Fetch GitHub user creation date via API",
  "checks": [
    "Form with id #github-form exists",
    "Element #created-at shows date"
  ]
}
```

## 🔐 Security

- Never commit `.env` files
- Use environment variables in production
- Rotate tokens if exposed
- Validate all inputs
- Use HTTPS in production

## 📖 Course Information

This project is part of:

- **Course**: Tools in Data Science (TDS)
- **Institution**: IIT Madras
- **Term**: September 2025

## 🤝 Contributing

This is a course project. Collaboration should follow course guidelines.

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

1. Check logs for errors
2. Review SETUP_GUIDE.md
3. Test individual components
4. Verify all credentials
5. Check API documentation:
   - AIPipe: https://aipipe.org/#documentation
   - GitHub: https://docs.github.com/rest

## 🎓 Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- GitHub API: https://docs.github.com/rest
- AIPipe: https://aipipe.org/#documentation
- Git: https://git-scm.com/doc

## 📈 Future Enhancements

- [ ] Background task queue (Celery/RQ)
- [ ] Database for task tracking
- [ ] Rate limiting
- [ ] Webhook verification
- [ ] Enhanced error notifications
- [ ] Support for multiple LLM providers
- [ ] Automated testing suite

## ✅ Submission Checklist

Before submitting to the course:

- [ ] Code is working locally
- [ ] All tests pass
- [ ] Deployed to production URL
- [ ] Environment variables configured
- [ ] API endpoint is publicly accessible
- [ ] GitHub token has correct permissions
- [ ] Secret matches form submission
- [ ] Tested with sample tasks

---

Made with ❤️ for TDS Course @ IIT Madras
