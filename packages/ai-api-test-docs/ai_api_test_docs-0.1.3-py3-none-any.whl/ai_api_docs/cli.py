import os
import re
import google.generativeai as genai
from dotenv import load_dotenv, set_key, unset_key
import textwrap
import mimetypes
import sys

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

model = None

def ensure_api_key():
    """Ensure Gemini API key is set, prompt and store if missing."""
    load_dotenv(ENV_PATH)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Gemini API key not found.")
        api_key = input("Please enter your Gemini API key: ").strip()
        if api_key:
            set_key(ENV_PATH, "GOOGLE_API_KEY", api_key)
            print("API key saved securely in .env file.")
        else:
            print("No API key provided. Exiting.")
            exit(1)
    return api_key

def delete_api_key():
    """Delete the stored Gemini API key from .env."""
    load_dotenv(ENV_PATH)
    if os.getenv("GOOGLE_API_KEY"):
        unset_key(ENV_PATH, "GOOGLE_API_KEY")
        print("API key deleted from .env.")
    else:
        print("No API key found to delete.")



def list_folders():
    """List directories and let user select one"""
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    if not folders:
        print("No folders found!")
        exit(1)
        
    print("Select a folder:")
    for idx, folder in enumerate(folders):
        print(f"{chr(97+idx)}. {folder}")
    
    choice = input("User input: ").strip().lower()
    try:
        return folders[ord(choice) - 97]
    except (IndexError, ValueError):
        print("Invalid choice.")
        exit(1)

def is_text_file(filepath):
    """Check if file is text-based"""
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('text/'):
        return True
    
    # Check common code extensions
    code_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', 
                       '.cs', '.cpp', '.h', '.swift', '.kt', '.rs', '.dart']
    if any(filepath.endswith(ext) for ext in code_extensions):
        return True
    
    # Check common config files
    config_files = ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 
                   'dockerfile', 'docker-compose.yml', '.env', 'config.yml']
    if any(filepath.endswith(f) for f in config_files):
        return True
    
    return False

def scan_project(folder_path, max_files=50, max_lines=200):
    """Scan project files and create context summary"""
    project_context = []
    file_count = 0
    
    # Prioritize key directories
    priority_dirs = ['app', 'src', 'lib', 'api', 'routes', 'controllers', 'views', 'test']
    priority_files = ['routes', 'urls', 'controllers', 'views', 'app', 'main', 'server']
    
    # Walk through project directory
    for root, _, files in os.walk(folder_path):
        # Skip virtual environments and hidden directories
        if any(part.startswith('.') or part in ('venv', 'env', 'node_modules') for part in root.split(os.sep)):
            continue
            
        # Prioritize key directories
        dir_priority = 1
        for pdir in priority_dirs:
            if pdir in root.split(os.sep):
                dir_priority = 3
                break
        
        for file in files:
            if file_count >= max_files:
                break
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, folder_path)
            
            # Skip binary files
            if not is_text_file(file_path):
                continue
                
            # Calculate file priority
            file_priority = dir_priority
            for pfile in priority_files:
                if pfile in file.lower():
                    file_priority = 5  # Highest priority
                    break
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        content.append(line)
                    file_content = ''.join(content)
                
                # Add to context with priority
                project_context.append({
                    'priority': file_priority,
                    'content': f"## File: {rel_path}\n{file_content}\n"
                })
                file_count += 1
            except Exception as e:
                print(f"Could not read {file_path}: {str(e)}")
    
    # Sort by priority (highest first)
    project_context.sort(key=lambda x: x['priority'], reverse=True)
    
    # Create context string
    context_str = "\n".join([item['content'] for item in project_context])
    
    # Summarize if too long
    if len(context_str) > 20000:
        print("Project context is large, summarizing with AI...")
        context_str = summarize_context(context_str)
    
    return context_str

def summarize_context(context_str):
    """Summarize large project context with AI"""
    prompt = textwrap.dedent(f"""
    You are an expert code analyzer. Summarize this project structure and codebase 
    focusing on key aspects for API documentation and test generation:
    
    - Application entry points
    - Routing configuration
    - Controller/View logic
    - Database models
    - Authentication mechanisms
    - Key dependencies
    
    Be concise but preserve critical details about API endpoints, their parameters, 
    and expected behaviors.
    
    Project context:
    {context_str[:30000]}  # Truncate to avoid token limits
    """)
    
    response = model.generate_content(prompt)
    return response.text

def ai_suggest_framework(context_str):
    """Detect framework using AI analysis"""
    prompt = textwrap.dedent(f"""
    Analyze the following project structure and codebase to determine the:
    1. Programming language
    2. Web framework
    3. Key libraries
    
    Respond in this EXACT format without additional text:
    Language: <language>
    Framework: <framework>
    Libraries: <comma-separated list>
    
    Project context:
    {context_str}
    """)
    
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)

def parse_ai_response(response_text):
    """Parse AI response into structured data"""
    result = {
        'language': 'Unknown',
        'framework': 'Unknown',
        'libraries': []
    }
    
    try:
        for line in response_text.split('\n'):
            if line.startswith('Language:'):
                result['language'] = line.split(':', 1)[1].strip()
            elif line.startswith('Framework:'):
                result['framework'] = line.split(':', 1)[1].strip()
            elif line.startswith('Libraries:'):
                libs = line.split(':', 1)[1].strip()
                result['libraries'] = [lib.strip() for lib in libs.split(',')]
    except Exception:
        pass
    
    return result

def generate_api_tests(context_str, tech_stack):
    """Generate API tests using AI with project context"""
    prompt = textwrap.dedent(f"""
    You are an expert QA engineer. Generate comprehensive API tests for the project below.
    
    Project Tech Stack:
    - Language: {tech_stack['language']}
    - Framework: {tech_stack['framework']}
    - Libraries: {', '.join(tech_stack['libraries'])}
    
    Requirements:
    1. Create tests for ALL API endpoints found in the code
    2. Cover success and error cases
    3. Include authentication tests where applicable
    4. Use appropriate testing libraries for the tech stack
    5. Include setup/teardown for database state
    6. Test all HTTP methods (GET, POST, PUT, DELETE, etc.)
    7. Validate response structures and status codes
    
    Project Context:
    {context_str}
    
    Output ONLY the test code without any explanations or markdown formatting. (do NOT include ```python or ```).
    """)
    
    response = model.generate_content(prompt)
    return response.text

def generate_api_docs(context_str, tech_stack):
    """Generate API documentation using AI with project context"""
    prompt = textwrap.dedent(f"""
    You are an expert technical writer. Generate comprehensive API documentation for the project below.
    
    Project Tech Stack:
    - Language: {tech_stack['language']}
    - Framework: {tech_stack['framework']}
    - Libraries: {', '.join(tech_stack['libraries'])}
    
    Requirements:
    1. Document ALL API endpoints
    2. For each endpoint:
       - HTTP method and path
       - Description
       - Parameters (query, path, body)
       - Request example -json
       - Response example (success and error)-json
       - Authentication requirements
    3. Include a table of contents
    4. Add sections for:
       - Authentication
       - Error codes
       - Rate limiting
       - Sample usage
    
    Project Context:
    {context_str}
    
    Output in Markdown format without any additional explanations.
    """)
    
    response = model.generate_content(prompt)
    return response.text

def write_file(folder_path, filename, content):
    """Write content to file in project directory"""
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filename} in {os.path.basename(folder_path)}")

def main():
    global model
    if len(sys.argv) > 1 and sys.argv[1] == "delete_key":
        delete_api_key()
        return
    
    api_key = ensure_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')

    # Load environment variables
    print("API Tools: Test Writer or Documentation Generator")
    print("a. Test Writer\nb. API Documentation")
    choice = input("User input: ").strip().lower()
    
    if choice not in ('a', 'b'):
        print("Invalid choice. Please select 'a' or 'b'")
        return
    
    # Select project folder
    folder_name = list_folders()
    folder_path = os.path.abspath(folder_name)
    
    # Scan project
    print(f"Scanning {folder_name}...")
    context = scan_project(folder_path)
    
    # Detect tech stack
    print("Analyzing project structure...")
    tech_stack = ai_suggest_framework(context)
    print(f"\nDetected Tech Stack:")
    print(f"Language: {tech_stack['language']}")
    print(f"Framework: {tech_stack['framework']}")
    print(f"Libraries: {', '.join(tech_stack['libraries'])}")
    
    # Generate content based on user choice
    if choice == 'a':
        print("Generating API tests...")
        tests = generate_api_tests(context, tech_stack)
        write_file(folder_path, "test_apis.py", tests)
    else:
        print("Generating API documentation...")
        docs = generate_api_docs(context, tech_stack)
        write_file(folder_path, "README.md", docs)

