import os
import requests
from typing import Dict, List, Optional
import json
import base64
import time

class LLMCodeGenerator:
    """Generates application code using AIPipe API based on task briefs."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AIPIPE_API_KEY")
        if not self.api_key:
            raise EnvironmentError("AIPIPE_API_KEY not set")
        self.base_url = "https://api.aipipe.org/v1/chat/completions"
    
    def _call_aipipe(self, prompt: str, max_tokens: int = 8000) -> str:
        """Make API call to AIPipe."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",  # or claude-3-opus-20240229
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # AIPipe follows OpenAI format
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            print(f"AIPipe API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def generate_app(
        self,
        brief: str,
        checks: List[str],
        attachments: List[Dict[str, str]],
        task_id: str,
        round_number: int = 1
    ) -> Dict[str, str]:
        """
        Generate application files using AIPipe.
        
        Returns:
            Dict with filenames as keys and content as values
            Example: {"index.html": "...", "README.md": "...", "LICENSE": "..."}
        """
        
        # Process attachments
        attachment_info = self._process_attachments(attachments)
        
        # Build the prompt
        prompt = self._build_prompt(brief, checks, attachment_info, task_id, round_number)
        
        # Call AIPipe API
        response_text = self._call_aipipe(prompt, max_tokens=8000)
        
        # Parse response to extract files
        files = self._parse_response(response_text, task_id, brief)
        
        return files
    
    def _process_attachments(self, attachments: List[Dict[str, str]]) -> str:
        """Process attachments and return formatted info for the prompt."""
        if not attachments:
            return "No attachments provided."
        
        info = ["Attachments provided:"]
        for att in attachments:
            name = att.get("name", "unknown")
            url = att.get("url", "")
            
            # Decode data URI if present
            if url.startswith("data:"):
                try:
                    # Extract content type and data
                    header, encoded = url.split(",", 1)
                    content_type = header.split(":")[1].split(";")[0]
                    
                    # Decode base64
                    decoded = base64.b64decode(encoded).decode('utf-8', errors='ignore')
                    
                    # Limit preview length
                    preview = decoded[:1000] if len(decoded) > 1000 else decoded
                    if len(decoded) > 1000:
                        preview += "\n... (truncated)"
                    
                    info.append(f"\n**{name}** ({content_type}):")
                    info.append(f"```\n{preview}\n```")
                except Exception as e:
                    info.append(f"\n**{name}**: [Could not decode: {e}]")
            else:
                info.append(f"\n**{name}**: {url}")
        
        return "\n".join(info)
    
    def _build_prompt(
        self,
        brief: str,
        checks: List[str],
        attachment_info: str,
        task_id: str,
        round_number: int
    ) -> str:
        """Build the prompt for the LLM."""
        
        checks_formatted = "\n".join([f"- {check}" for check in checks])
        
        prompt = f"""You are building a single-page web application for GitHub Pages deployment.

**Task ID**: {task_id}
**Round**: {round_number}

**Brief**:
{brief}

**Requirements/Checks** (your app MUST pass these):
{checks_formatted}

**Attachments**:
{attachment_info}

**Instructions**:
1. Generate a COMPLETE, FUNCTIONAL single-page application (HTML/CSS/JS)
2. Use CDN links for any libraries (Bootstrap, marked, highlight.js, Papaparse for CSV, etc.)
3. The app must be self-contained in index.html (embed all CSS/JS or use minimal additional files)
4. Handle attachments by embedding data URIs directly in the code or parsing them
5. Implement ALL functionality described in the brief
6. Add proper error handling and user feedback
7. Make it visually appealing with Bootstrap 5 or modern CSS
8. Ensure all checks can pass when tested
9. Use semantic HTML and accessible design

**CRITICAL REQUIREMENTS**: 
- NEVER use localStorage or sessionStorage (not supported in evaluation environment)
- Use in-memory JavaScript variables/objects for any state management
- All data must be stored in JavaScript variables only
- If attachments contain CSV data, parse it using Papaparse CDN
- If attachments contain JSON, parse it directly in JavaScript
- Make sure all IDs mentioned in checks exist in your HTML

**Output Format**:
Provide the files in this EXACT format with clear markers:

FILE: index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Your complete HTML here -->
</head>
<body>
    <!-- Your content here -->
</body>
</html>
```

FILE: README.md
```markdown
# {task_id}

## Summary
[Brief description]

## Setup & Usage
[How to use the application]

## Features
[List of features]

## Code Explanation
[Explain the key parts of the code]

## License
MIT License
```

FILE: LICENSE
```
MIT License

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
SOFTWARE.
```

Generate the complete application now. Make sure it's production-ready and will pass all checks."""
        
        return prompt
    
    def _parse_response(self, response_text: str, task_id: str, brief: str) -> Dict[str, str]:
        """Parse LLM response to extract files."""
        files = {}
        
        # Split by FILE: markers
        parts = response_text.split("FILE: ")
        
        for part in parts[1:]:  # Skip first empty part
            lines = part.strip().split("\n", 1)
            if len(lines) < 2:
                continue
            
            filename = lines[0].strip()
            content = lines[1].strip()
            
            # Remove code block markers
            if content.startswith("```"):
                # Find language identifier and remove it
                first_newline = content.find("\n")
                if first_newline != -1:
                    content = content[first_newline + 1:]
                # Remove closing ```
                if content.endswith("```"):
                    content = content[:-3].strip()
            
            files[filename] = content
        
        # Fallback: try to extract HTML if FILE markers weren't used
        if "index.html" not in files:
            if "<!DOCTYPE html>" in response_text or "<html" in response_text:
                start = response_text.find("<!DOCTYPE html>")
                if start == -1:
                    start = response_text.find("<html")
                end = response_text.rfind("</html>") + 7
                if start != -1 and end > start:
                    files["index.html"] = response_text[start:end]
        
        # Ensure we have required files
        if "LICENSE" not in files:
            files["LICENSE"] = self._get_mit_license()
        
        if "README.md" not in files:
            files["README.md"] = self._get_default_readme(task_id, brief)
        
        return files
    
    def _get_mit_license(self) -> str:
        """Return standard MIT license text."""
        return """MIT License

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
    
    def _get_default_readme(self, task_id: str, brief: str) -> str:
        """Return default README template."""
        return f"""# {task_id}

## Summary
This application was automatically generated to fulfill the project requirements.

**Brief**: {brief}

## Setup & Usage
This is a static web application deployed on GitHub Pages.

1. Visit the GitHub Pages URL
2. The application will load automatically
3. Follow on-screen instructions

## Features
- Implements all requirements from the brief
- Responsive design
- Error handling
- Modern UI/UX

## Code Explanation
The application is built as a single-page application using vanilla JavaScript and HTML/CSS.
All functionality is self-contained in `index.html`.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
"""

    def revise_app(
        self,
        brief: str,
        checks: List[str],
        attachments: List[Dict[str, str]],
        task_id: str,
        existing_code: str
    ) -> Dict[str, str]:
        """
        Revise existing application for Round 2.
        
        Args:
            brief: New requirements
            checks: New checks to pass
            attachments: New attachments
            task_id: Task identifier
            existing_code: Current index.html content
            
        Returns:
            Updated files
        """
        attachment_info = self._process_attachments(attachments)
        checks_formatted = "\n".join([f"- {check}" for check in checks])
        
        # Truncate existing code if too long
        code_preview = existing_code
        if len(existing_code) > 10000:
            code_preview = existing_code[:10000] + "\n... (truncated for brevity)"
        
        prompt = f"""You are revising an existing web application for Round 2.

**Task ID**: {task_id}
**Round**: 2

**New Requirements**:
{brief}

**New Checks** (app MUST pass these):
{checks_formatted}

**New/Additional Attachments**:
{attachment_info}

**Current Code**:
```html
{code_preview}
```

**Instructions**:
1. MODIFY the existing code to add the new features
2. Keep ALL existing functionality intact unless it conflicts with new requirements
3. Maintain the same structure, style, and design consistency
4. Ensure all NEW checks can pass while keeping old functionality working
5. Update inline comments to explain what changed
6. DO NOT use localStorage or sessionStorage
7. Add the new functionality seamlessly

**Output Format**:
FILE: index.html
```html
[complete updated HTML content with new features]
```

FILE: README.md
```markdown
[updated README with a "Round 2 Changes" section at the end]
```

Generate the revised application now. Make it production-ready."""
        
        response_text = self._call_aipipe(prompt, max_tokens=8000)
        return self._parse_response(response_text, task_id, brief)