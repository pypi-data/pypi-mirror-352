# ==================== TOOLS MODULE ====================
# zeuslab/hercules/tools.py

import os
import json
import requests
import subprocess
from typing import Any, Dict, List, Optional, Annotated
from datetime import datetime
import sqlite3
import csv
import io

def write_file(filename: str, content: str, mode: str = 'w') -> str:
    """
    Write content to a file
    
    Args:
        filename: Path to the file
        content: Content to write
        mode: Write mode ('w' for write, 'a' for append)
    
    Returns:
        Success message or error
    """
    try:
        with open(filename, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def read_file(filename: str) -> str:
    """
    Read content from a file
    
    Args:
        filename: Path to the file
    
    Returns:
        File content or error message
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"
def list_files(directory: Annotated[str, "Directory path to list files from"] = ".") -> str:
    """List files in a directory."""
    try:
        path = Path(directory)
        if not path.exists():
            return f"Directory {directory} does not exist."
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                files.append(f"📄 {item.name}")
            elif item.is_dir():
                files.append(f"📁 {item.name}/")
        
        if not files:
            return f"Directory {directory} is empty."
        
        return f"Contents of {directory}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files in {directory}: {str(e)}"

def web_search(query: str, num_results: int = 5) -> str:
    """
    Perform a web search (mock implementation - replace with actual search API)
    
    Args:
        query: Search query
        num_results: Number of results to return
    
    Returns:
        Search results as formatted string
    """
    # This is a mock implementation - replace with actual search API
    try:
        # You would integrate with Google Search API, Bing API, or similar
        results = {
            "query": query,
            "results": [
                {
                    "title": f"Result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a sample search result snippet {i+1} for the query '{query}'"
                }
                for i in range(num_results)
            ]
        }
        
        formatted_results = f"Search Results for '{query}':\n\n"
        for i, result in enumerate(results["results"], 1):
            formatted_results += f"{i}. {result['title']}\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   {result['snippet']}\n\n"
        
        return formatted_results
    except Exception as e:
        return f"Error performing web search: {str(e)}"

def execute_python_code(code: str) -> str:
    """
    Execute Python code safely
    
    Args:
        code: Python code to execute
    
    Returns:
        Execution result or error
    """
    try:
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code
        result = subprocess.run(['python', temp_file], 
                              capture_output=True, text=True, timeout=30)
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return f"Execution successful:\n{result.stdout}"
        else:
            return f"Execution error:\n{result.stderr}"
    except Exception as e:
        return f"Error executing code: {str(e)}"

def create_database(db_name: str, schema: Dict[str, List[str]]) -> str:
    """
    Create a SQLite database with given schema
    
    Args:
        db_name: Database filename
        schema: Dictionary with table names as keys and column definitions as values
    
    Returns:
        Success message or error
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        for table_name, columns in schema.items():
            columns_str = ', '.join(columns)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
        
        conn.commit()
        conn.close()
        return f"Database '{db_name}' created successfully with tables: {list(schema.keys())}"
    except Exception as e:
        return f"Error creating database: {str(e)}"

def query_database(db_name: str, query: str) -> str:
    """
    Execute a SQL query on a database
    
    Args:
        db_name: Database filename
        query: SQL query to execute
    
    Returns:
        Query results or error
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # Format results as table
            if results:
                formatted_results = f"Query: {query}\n\n"
                formatted_results += " | ".join(columns) + "\n"
                formatted_results += "-" * (len(" | ".join(columns))) + "\n"
                for row in results:
                    formatted_results += " | ".join(str(cell) for cell in row) + "\n"
                return formatted_results
            else:
                return "Query executed successfully. No results returned."
        else:
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Error executing query: {str(e)}"
    finally:
        conn.close()

def send_email(to: str, subject: str, body: str, smtp_config: Optional[Dict] = None) -> str:
    """
    Send an email (mock implementation)
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        smtp_config: SMTP configuration
    
    Returns:
        Success message or error
    """
    # Mock implementation - replace with actual email sending
    try:
        # You would use smtplib here for actual email sending
        email_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        return f"Email sent successfully to {to} with subject '{subject}'"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def parse_csv(file_path: str, delimiter: str = ',') -> str:
    """
    Parse CSV file and return structured data
    
    Args:
        file_path: Path to CSV file
        delimiter: CSV delimiter
    
    Returns:
        Parsed CSV data or error
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            data = list(reader)
        
        result = f"CSV file '{file_path}' parsed successfully.\n"
        result += f"Rows: {len(data)}\n"
        result += f"Columns: {list(data[0].keys()) if data else []}\n\n"
        
        # Show first few rows
        for i, row in enumerate(data[:3]):
            result += f"Row {i+1}: {row}\n"
        
        if len(data) > 3:
            result += f"... and {len(data) - 3} more rows"
        
        return result
    except Exception as e:
        return f"Error parsing CSV: {str(e)}"

def make_http_request(url: str, method: str = 'GET', headers: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> str:
    """
    Make HTTP request
    
    Args:
        url: Request URL
        method: HTTP method
        headers: Request headers
        data: Request data for POST/PUT
    
    Returns:
        Response data or error
    """
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            json=data,
            timeout=30
        )
        
        result = f"HTTP {method.upper()} request to {url}\n"
        result += f"Status Code: {response.status_code}\n"
        result += f"Response Headers: {dict(response.headers)}\n\n"
        
        try:
            # Try to parse as JSON
            json_data = response.json()
            result += f"Response Body (JSON):\n{json.dumps(json_data, indent=2)}"
        except:
            # Fall back to text
            result += f"Response Body (Text):\n{response.text[:1000]}"
            if len(response.text) > 1000:
                result += "... (truncated)"
        
        return result
    except Exception as e:
        return f"Error making HTTP request: {str(e)}"

# Default tools collection
DEFAULT_TOOLS = [
    write_file,
    read_file,
    list_files,
    web_search,
    execute_python_code,
    create_database,
    query_database,
    send_email,
    parse_csv,
    make_http_request
]

# Tools categories for easy selection
FILE_TOOLS = [write_file, read_file,list_files, parse_csv]
WEB_TOOLS = [web_search, make_http_request]
DATABASE_TOOLS = [create_database, query_database]
CODE_TOOLS = [execute_python_code]
COMMUNICATION_TOOLS = [send_email]
