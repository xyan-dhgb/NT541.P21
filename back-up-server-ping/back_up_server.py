#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import logging
import os

# Initialize project path
PROJECT_PATH = 'ENTER-YOUR-PATH-HERE'  # Replace with your project path

# Initialize logging
logging.basicConfig(
    filename=os.path.join(PROJECT_PATH, 'server.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Flask_Server')

app = Flask(__name__)

@app.route('/')
def index():
    """Return different content based on source IP"""
    client_ip = request.remote_addr
    logger.info("Request from IP: {}".format(client_ip))
    
    # Check IP to determine user type
    if client_ip.startswith('10.0.10.'):
        logger.info("Returning content for Student")
        return "Chào Student!"
    elif client_ip.startswith('10.0.20.'):
        logger.info("Returning content for Teacher")
        return "Chào Teacher!"
    elif client_ip.startswith('10.0.30.'):
        logger.info("Returning content for Staff")
        return "Chào Staff!"
    else:
        logger.info("Unknown IP: {}, returning default content".format(client_ip))
        return "Xin chào! IP của bạn là {}".format(client_ip)

if __name__ == '__main__':
    logger.info("Start Flask server")
    # Listen on all interfaces
    app.run(host='0.0.0.0', port=8080, debug=True) 