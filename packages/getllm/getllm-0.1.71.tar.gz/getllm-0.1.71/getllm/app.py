#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyLLM Application Entry Point

This module serves as the entry point for the PyLLM service.
It provides a REST API for LLM operations.
"""

import argparse
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Initialize logging with LogLama
from getllm.logging_config import init_logging, get_logger

# Initialize logging first, before any other imports
init_logging()

# Get a logger for this module
logger = get_logger('app')

class PyLLMHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'ok',
                'message': 'PyLLM service is healthy'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'message': 'Not found'
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                prompt = data.get('prompt', '')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'output': f'Dummy response to prompt: {prompt[:50]}...',
                    'error': None
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'error',
                    'message': str(e)
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'message': 'Not found'
            }
            self.wfile.write(json.dumps(response).encode())

def run_server(host='127.0.0.1', port=8001):
    server_address = (host, port)
    httpd = HTTPServer(server_address, PyLLMHandler)
    logger.info(f'Starting PyLLM server on {host}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Stopping PyLLM server')
        httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description='PyLLM - LLM Operations Service')
    parser.add_argument('--port', type=int, default=8001, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
