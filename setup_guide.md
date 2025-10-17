# Setup Guide for TDS Project 1

## Prerequisites

1. **Python 3.8+** installed
2. **Git** installed and configured
3. **GitHub Account** with a Personal Access Token
4. **AIPipe Account** with API key

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tds_25t3_P1.git
cd tds_25t3_P1
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your API Keys

#### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "TDS Project 1"
4. Select scopes: `repo`, `workflow`
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

#### AIPipe Token
1. Go to https://aipipe.org/
2. Sign up or log in
3. Navigate to your dashboard/API keys section
4. Copy your API key

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AIPIPE_API_KEY=your_aipipe_key_here
SECRET=ljao(23$*dfs#1023-49($HC9203*&(23
```

**⚠️ IMPORTANT**: Never commit the `.env` file to git! It's already in `.gitignore`.

### 6. Test Locally

Start the server:

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

### 7. Test with Sample Request

Open a new terminal and run:

```bash
curl -X POST http://localhost:8000/initiate_task \
-H "Content-Type: application/json" \
-d '{
  "email": "your-email@example.com",
  "secret": "ljao(23$*dfs#1023-49($HC9203*&(23",
  "task": "test-task-001",
  "round": 1,
  "nonce": "test-nonce-123",
  "brief": "Create a simple Bootstrap page with a centered heading and a button.",
  "checks": [
    "Page has Bootstrap CSS loaded",
    "Page has a heading element",
    "Page has a button element"
  ],
  "evaluation_url": "https://webhook.site/your-webhook-id",
  "attachments": []
}'
```

**Tip**: Use https://webhook.site/ to create a temporary endpoint for testing.

## Deployment Options

### Option 1: Deploy on Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Railway dashboard:
   - `GITHUB_TOKEN`
   - `AIPIPE_API_KEY`
   - `SECRET`
6. Railway will auto-deploy

### Option 2: Deploy on Render

1. Go to https://render.com/
2. Sign up and create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py`
6. Add environment variables
7. Deploy

### Option 3: Deploy on Your Own Server

```bash
# Install on Ubuntu/Debian server
sudo apt update
sudo apt install python3 python3-pip git

# Clone and setup
git clone https://github.com/your-username/tds_25t3_P1.git
cd tds_25t3_P1
pip3 install -r requirements.txt

# Create .env file with your credentials

# Run with nohup
nohup python3 main.py > server.log 2>&1 &
```

## Submitting to the Course

1. Deploy your application to a public URL (e.g., Railway, Render)
2. Test your endpoint is publicly accessible
3. Fill out the Google Form with:
   - Your API endpoint URL (e.g., `https://your-app.railway.app/initiate_task`)
   - Your secret
   - Your GitHub username

## Troubleshooting

### Issue: "GITHUB_TOKEN not set"
- Make sure your `.env` file exists and has the correct token
- Restart the server after adding the token

### Issue: "AIPIPE_API_KEY not set"
- Verify you've added the correct AIPipe API key to `.env`
- Check for typos in the key

### Issue: Git commands fail
- Run: `git config --global user.email "you@example.com"`
- Run: `git config --global user.name "Your Name"`

### Issue: Repository creation fails
- Check your GitHub token has `repo` scope
- Verify token hasn't expired
- Check GitHub API rate limits

### Issue: LLM generation fails
- Check AIPipe API key is valid
- Verify you have credits/quota on AIPipe
- Check the logs for specific error messages

### Issue: GitHub Pages not deploying
- Wait 2-3 minutes after repo creation
- Check repo settings on GitHub
- Verify the `main` branch exists with code

## Testing the Full Flow

1. Start your server
2. Send a Round 1 request
3. Wait for completion (check logs)
4. Verify the GitHub repo was created
5. Check GitHub Pages is live (may take 2-3 minutes)
6. Send a Round 2 request with the same task ID
7. Verify changes are reflected

## Monitoring

Check the logs for debugging:

```bash
# If running directly
# Output is in the console

# If running with nohup
tail -f server.log

# If on Railway/Render
# Check the deployment logs in their dashboard
```

## Security Notes

1. **Never commit `.env`** - it contains sensitive tokens
2. **Use environment variables** in production, not `.env` files
3. **Rotate tokens** if they're exposed
4. **Use HTTPS** for production deployments
5. **Validate all inputs** before processing

## Next Steps

- Test with various task types (CSV, Markdown, GitHub API)
- Monitor your AIPipe usage/credits
- Set up error notifications
- Add rate limiting if needed
- Implement proper background task processing

## Support

If you encounter issues:
1. Check the logs first
2. Verify all credentials are correct
3. Test each component individually
4. Review the AIPipe documentation: https://aipipe.org/#documentation
5. Check GitHub API status: https://www.githubstatus.com/