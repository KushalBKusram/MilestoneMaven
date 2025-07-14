import os
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from services.trmnl_service import TrmnlService
from services.countdown_service import CountdownService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize services
countdown_service = CountdownService()
trmnl_service = TrmnlService(countdown_service)

@app.route('/')
def index():
    """Main page showing countdown management UI"""
    countdowns = countdown_service.get_all_countdowns()
    return render_template('countdown.html', countdowns=countdowns)

@app.route('/api/countdowns', methods=['POST'])
def add_countdown():
    """Add a new countdown item"""
    try:
        data = request.get_json()
        title = data.get('title')
        target_date = data.get('target_date')
        
        if not title or not target_date:
            return jsonify({'error': 'Title and target_date are required'}), 400
        
        countdown_id = countdown_service.add_countdown(title, target_date)
        return jsonify({'id': countdown_id, 'message': 'Countdown added successfully'}), 201
    
    except Exception as e:
        logger.error(f"Error adding countdown: {e}")
        return jsonify({'error': 'Failed to add countdown'}), 500

@app.route('/api/countdowns/<countdown_id>', methods=['PUT'])
def update_countdown(countdown_id):
    """Update an existing countdown item"""
    try:
        data = request.get_json()
        title = data.get('title')
        target_date = data.get('target_date')
        
        if not title or not target_date:
            return jsonify({'error': 'Title and target_date are required'}), 400
        
        success = countdown_service.update_countdown(countdown_id, title, target_date)
        if success:
            return jsonify({'message': 'Countdown updated successfully'}), 200
        else:
            return jsonify({'error': 'Countdown not found'}), 404
    
    except Exception as e:
        logger.error(f"Error updating countdown: {e}")
        return jsonify({'error': 'Failed to update countdown'}), 500

@app.route('/api/countdowns/<countdown_id>', methods=['DELETE'])
def delete_countdown(countdown_id):
    """Delete a countdown item"""
    try:
        success = countdown_service.delete_countdown(countdown_id)
        if success:
            return jsonify({'message': 'Countdown deleted successfully'}), 200
        else:
            return jsonify({'error': 'Countdown not found'}), 404
    
    except Exception as e:
        logger.error(f"Error deleting countdown: {e}")
        return jsonify({'error': 'Failed to delete countdown'}), 500

@app.route('/api/countdowns', methods=['GET'])
def get_countdowns():
    """Get all countdown items"""
    try:
        countdowns = countdown_service.get_all_countdowns()
        return jsonify(countdowns), 200
    
    except Exception as e:
        logger.error(f"Error getting countdowns: {e}")
        return jsonify({'error': 'Failed to get countdowns'}), 500

def start_trmnl_service():
    """Start the TRMNL service in a separate thread"""
    logger.info("Starting TRMNL service...")
    trmnl_thread = threading.Thread(target=trmnl_service.start, daemon=True)
    trmnl_thread.start()
    logger.info("TRMNL service started successfully")

if __name__ == '__main__':
    # Start TRMNL service
    start_trmnl_service()
    
    # Run Flask app
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=False)
