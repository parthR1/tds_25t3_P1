import os
import json
import logging
import shutil
import subprocess
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
import requests

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN environment variable not set.")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    On startup, find and log the .env file path for debugging.
    """
    from dotenv import find_dotenv
    dotenv_path = find_dotenv()
    if not dotenv_path:
        logger.warning(".env file not found. The script will rely on global environment variables.")
    else:
        logger.info(f"Found .env file at: {dotenv_path}")

# --- Helper Functions ---

def run_command(command, cwd=None):
    """Executes a shell command and returns its output."""
    logger.info(f"Running command: {' '.join(command)} in {cwd or os.getcwd()}")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Stdout: {e.stdout}")
        raise

def get_github_username():
    """Fetches the GitHub username associated with the GITHUB_TOKEN."""
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        response.raise_for_status()
        user_data = response.json()
        username = user_data.get("login")
        logger.info(f"GitHub username: {username}")
        return username
    except requests.RequestException as e:
        logger.error(f"Failed to get GitHub username: {e}")
        raise

def create_github_repo(repo_name, temp_dir, owner):
    """Create a GitHub repository using the API and push code."""
    
    # 1. Create repo via API
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "name": repo_name,
        "private": False,
        "auto_init": False
    }
    
    logger.info(f"Creating repository: {repo_name}")
    response = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        logger.info(f"Repository {repo_name} created successfully")
        repo_data = response.json()
        clone_url = repo_data["clone_url"]
        html_url = repo_data["html_url"]
    elif response.status_code == 422:
        logger.warning(f"Repository {repo_name} already exists")
        clone_url = f"https://github.com/{owner}/{repo_name}.git"
        html_url = f"https://github.com/{owner}/{repo_name}"
    else:
        logger.error(f"Failed to create repository: {response.text}")
        raise Exception(f"Repository creation failed: {response.status_code} - {response.text}")
    
    # 2. Add remote and push
    # Use token in URL for authentication
    authenticated_url = clone_url.replace(
        "https://",
        f"https://{GITHUB_TOKEN}@"
    )
    
    run_command(["git", "remote", "add", "origin", authenticated_url], cwd=temp_dir)
    run_command(["git", "push", "-u", "origin", "main"], cwd=temp_dir)
    
    logger.info(f"Code pushed to repository: {html_url}")
    return html_url

def enable_github_pages(owner, repo_name):
    """Enable GitHub Pages for the repository."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    logger.info(f"Enabling GitHub Pages for {owner}/{repo_name}")
    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo_name}/pages",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        logger.info("GitHub Pages enabled successfully")
        return True
    elif response.status_code == 409:
        logger.warning("GitHub Pages already enabled")
        return True
    else:
        logger.error(f"Failed to enable GitHub Pages: {response.status_code} - {response.text}")
        # Don't raise exception, as this is not critical
        return False

def submit_evaluation(payload, url):
    """Submits the evaluation payload with retry logic."""
    max_retries = 5
    delay = 1  # Initial delay in seconds
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Evaluation submitted successfully to {url}. Status: {response.status_code}")
            return
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
    logger.error("Failed to submit evaluation after all retries.")
    raise Exception("Failed to submit evaluation.")


# --- Core Logic ---

def round1(task_data: dict):
    """
    Handles the logic for building and deploying a new application for Round 1.
    """
    logger.info(f"Processing Round 1 for task: {task_data.get('task')}")
    
    brief = task_data.get("brief", "No brief provided.")
    task_id = task_data.get("task")
    nonce = task_data.get("nonce")
    evaluation_url = task_data.get("evaluation_url")
    repo_name = f"tds-project-1-{task_id.replace(' ', '-').lower()}"
    temp_dir = os.path.join(os.getcwd(), f"temp_app_{nonce}")

    try:
        # 1. Get GitHub username
        owner = get_github_username()
        logger.info(f"GitHub user: {owner}")

        # 2. Create a temporary directory for the new app
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # 3. Generate Application Files (LLM-assisted)
        # For this example, we generate a simple index.html based on the brief.
        index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{task_id}</title>
</head>
<body>
    <h1>Task: {task_id}</h1>
    <p>Brief: {brief}</p>
</body>
</html>"""
        with open(os.path.join(temp_dir, "index.html"), "w") as f:
            f.write(index_html_content)

        # Generate LICENSE
        license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
        with open(os.path.join(temp_dir, "LICENSE"), "w") as f:
            f.write(license_content)

        # Generate README.md
        readme_content = f"""# {repo_name}

## Summary
This repository was auto-generated to fulfill the requirements of the task: `{task_id}`.
The application brief was: "{brief}".

## Setup & Usage
This is a static web page deployed using GitHub Pages.

## Code Explanation
The `index.html` file contains the main content of the page, generated based on the project brief.

## License
This project is licensed under the MIT License.
"""
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write(readme_content)

        # 4. Initialize Git repository
        run_command(["git", "init"], cwd=temp_dir)
        run_command(["git", "add", "."], cwd=temp_dir)
        run_command(["git", "commit", "-m", "Initial commit"], cwd=temp_dir)
        
        # 5. Create GitHub repo and push
        repo_url = create_github_repo(repo_name, temp_dir, owner)
        
        # 6. Get commit SHA
        commit_sha = run_command(["git", "rev-parse", "HEAD"], cwd=temp_dir)
        
        # 7. Enable GitHub Pages
        enable_github_pages(owner, repo_name)
        logger.info("GitHub Pages enabled. It may take a few minutes for the site to become available.")

        # 8. Prepare and Submit Evaluation
        pages_url = f"https://{owner}.github.io/{repo_name}/"

        evaluation_payload = {
            "email": task_data.get("email"),
            "task": task_id,
            "round": 1,
            "nonce": nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        
        logger.info(f"Submitting evaluation payload: {json.dumps(evaluation_payload, indent=2)}")
        submit_evaluation(evaluation_payload, evaluation_url)

    finally:
        # 9. Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")

def round2(task_data: dict):
    """
    Handles the logic for revising an existing application for Round 2.
    """
    logger.info(f"Processing Round 2 for task: {task_data.get('task')}")

    brief = task_data.get("brief", "No brief provided for revision.")
    task_id = task_data.get("task")
    nonce = task_data.get("nonce")
    evaluation_url = task_data.get("evaluation_url")
    repo_name = f"tds-project-1-{task_id.replace(' ', '-').lower()}"
    temp_dir = os.path.join(os.getcwd(), f"temp_app_round2_{nonce}")

    try:
        # 1. Get GitHub username and set up repo URL
        owner = get_github_username()
        repo_url = f"https://{owner}:{GITHUB_TOKEN}@github.com/{owner}/{repo_name}.git"
        logger.info(f"Target repository: {repo_name}")

        # 2. Clone the existing repository
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        run_command(["git", "clone", repo_url, temp_dir])

        # 3. Modify Application Files (LLM-assisted revision)
        # Modify index.html to include the revision
        index_html_path = os.path.join(temp_dir, "index.html")
        with open(index_html_path, "a") as f:
            f.write(f"\n<hr><h2>Round 2 Revision</h2><p>{brief}</p>")

        # Modify README.md to log the revision
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, "a") as f:
            f.write(f"\n\n## Round 2 Changes\n- Applied revision: \"{brief}\"")

        # 4. Commit and Push Changes
        run_command(["git", "config", "user.email", "action@github.com"], cwd=temp_dir)
        run_command(["git", "config", "user.name", "GitHub Action"], cwd=temp_dir)
        run_command(["git", "add", "."], cwd=temp_dir)
        run_command(["git", "commit", "-m", "Apply revisions for Round 2"], cwd=temp_dir)
        run_command(["git", "push"], cwd=temp_dir)
        logger.info("Pushed changes to GitHub.")

        # 5. Prepare and Submit Evaluation for Round 2
        commit_sha = run_command(["git", "rev-parse", "HEAD"], cwd=temp_dir)
        pages_url = f"https://{owner}.github.io/{repo_name}/"

        evaluation_payload = {
            "email": task_data.get("email"),
            "task": task_id,
            "round": 2,
            "nonce": nonce,
            "repo_url": f"https://github.com/{owner}/{repo_name}",
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }

        logger.info(f"Submitting evaluation payload for Round 2: {json.dumps(evaluation_payload, indent=2)}")
        submit_evaluation(evaluation_payload, evaluation_url)

    finally:
        # 6. Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")


# --- API Endpoint ---

def validate_secret(secret: str) -> bool:
    # This should be replaced with a more secure validation method.
    return secret == "ljao(23$*dfs#1023-49($HC9203*&(23"

@app.post("/initiate_task")
async def initiate_task(request: Request):
    """
    Main endpoint to receive tasks, validate them, and dispatch to the correct round handler.
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    required_fields = ["secret", "round", "task", "evaluation_url", "email", "nonce"]
    if not all(field in data for field in required_fields):
        missing = [field for field in required_fields if field not in data]
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    if not validate_secret(data.get("secret", "")):
        raise HTTPException(status_code=403, detail="Invalid secret.")

    round_number = data.get("round")
    
    # Run tasks in the background to avoid blocking the response
    if round_number == 1:
        # For simplicity in this interactive CLI, we run it directly.
        # In a real scenario, you'd use background tasks (e.g., with Celery or FastAPI's BackgroundTasks).
        try:
            round1(data)
        except Exception as e:
            logger.error(f"An error occurred during Round 1 processing: {e}")
            # In a real app, you might want to notify an admin or have a retry mechanism.
            raise HTTPException(status_code=500, detail="An internal error occurred during task processing.")

    elif round_number == 2:
        round2(data)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid round number: {round_number}")

    return {"message": "Task initiation acknowledged successfully."}

if __name__ == '__main__':
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host='0.0.0.0', port=52128)