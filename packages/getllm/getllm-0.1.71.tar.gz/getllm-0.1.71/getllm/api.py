#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyLLM API - REST API for LLM operations

This module provides a FastAPI server for interacting with LLM models.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from getllm.models import ModelManager

# Create FastAPI app
app = FastAPI(
    title="PyLLM API",
    description="""
    # PyLLM API
    
    API for LLM operations and code fixing capabilities.
    
    ## Features
    
    * Query LLM models with custom prompts
    * Fix Python code using LLM-powered analysis
    * Support for multiple fix attempts with different strategies
    * Health check endpoint for monitoring
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Models for request/response
class QueryRequest(BaseModel):
    prompt: str
    model: str = "llama3"
    max_tokens: int = 1000
    temperature: float = 0.7

class CodeFixRequest(BaseModel):
    code: str
    error_message: str
    is_logic_error: bool = False
    attempt: int = 1
    prompt_type: Optional[str] = None

# Helper function to extract Python code from LLM response
def extract_python_code(text):
    """Extract Python code from markdown code blocks."""
    if not text:
        return ""
    
    # Look for Python code blocks
    lines = text.split('\n')
    in_code_block = False
    code_lines = []
    
    for line in lines:
        if line.strip().startswith('```python'):
            in_code_block = True
            continue
        elif line.strip().startswith('```') and in_code_block:
            in_code_block = False
            continue
        
        if in_code_block:
            code_lines.append(line)
    
    # If no code blocks found, try to extract any code-like content
    if not code_lines:
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('```'):
                code_lines.append(line)
    
    return '\n'.join(code_lines)

# API endpoints
@app.post("/query", tags=["llm"])
async def query_model(request: QueryRequest):
    """Query an LLM model with a prompt"""
    try:
        manager = ModelManager()
        response = manager.query(
            request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fix-code", tags=["code"])
async def fix_code(request: CodeFixRequest):
    """Fix Python code using LLM"""
    try:
        manager = ModelManager()
        
        # Determine the prompt based on the request
        if request.attempt == 1:
            if request.is_logic_error:
                prompt = f"""Fix the following Python code that has a logical error:

```python
{request.code}
```

The code runs without errors but produces incorrect results. The issue is: {request.error_message}

Specifically, look for comments that indicate where the logical error is and fix that part.

Please provide only the fixed code as a Python code block. Make sure to include all necessary imports.

Your fixed code should be complete and runnable."""
            else:
                prompt = f"""Fix the following Python code that has an error:

```python
{request.code}
```

Error message: {request.error_message}

Please provide only the fixed code as a Python code block. Make sure to include all necessary imports.

If the error is about missing imports, make sure to add the appropriate import statements at the top of the code.

Your fixed code should be complete and runnable."""
        elif request.attempt == 2:
            # Second attempt with more specific error handling
            if "ModuleNotFoundError" in request.error_message or "ImportError" in request.error_message:
                prompt = f"""Fix the following Python code that has an import error:

```python
{request.code}
```

Error message: {request.error_message}

Please focus on fixing the imports. Consider using standard library alternatives if a package is not available.
Provide only the fixed code as a Python code block."""
            elif "SyntaxError" in request.error_message:
                prompt = f"""Fix the following Python code that has a syntax error:

```python
{request.code}
```

Error message: {request.error_message}

Please carefully check for syntax issues like missing colons, parentheses, or indentation.
Provide only the fixed code as a Python code block."""
            else:
                prompt = f"""Fix the following Python code that still has an error after a previous fix attempt:

```python
{request.code}
```

Error message: {request.error_message}

Please try a completely different approach to fix this code.
Provide only the fixed code as a Python code block."""
        elif request.attempt == 3:
            # Third attempt with a complete rewrite approach
            prompt = f"""This Python code has been fixed twice but still has errors:

```python
{request.code}
```

Error message: {request.error_message}

Please rewrite this code completely from scratch to achieve the same goal but with a simpler approach.
Focus on using only the standard library and basic Python features.
Provide only the fixed code as a Python code block."""
        else:
            raise HTTPException(status_code=400, detail="Invalid attempt number")
        
        # Override prompt if prompt_type is specified
        if request.prompt_type:
            if request.prompt_type == "second_attempt":
                prompt = f"""Fix the following Python code that still has an error after a previous fix attempt:

```python
{request.code}
```

Error message: {request.error_message}

Please try a completely different approach to fix this code.
Provide only the fixed code as a Python code block."""
            elif request.prompt_type == "third_attempt":
                prompt = f"""This Python code has been fixed twice but still has errors:

```python
{request.code}
```

Error message: {request.error_message}

Please rewrite this code completely from scratch to achieve the same goal but with a simpler approach.
Focus on using only the standard library and basic Python features.
Provide only the fixed code as a Python code block."""
        
        # Query the model
        response = manager.query(prompt)
        
        # Extract the fixed code
        fixed_code = extract_python_code(response)
        
        return {"fixed_code": fixed_code, "full_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["system"], response_model=Dict[str, str])
async def health_check():
    """
    Check if the API is running
    
    This endpoint provides a simple health check to verify that the API is operational.
    It can be used by monitoring systems to check the service status.
    
    Example response:
    ```json
    {
        "status": "healthy",
        "version": "0.1.0",
        "service": "PyLLM API"
    }
    ```
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "PyLLM API"
    }

def start_server(host="0.0.0.0", port=8001):
    """Start the PyLLM API server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
