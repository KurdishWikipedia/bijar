# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - API Routes
This file defines all the API endpoints for the Flask application using a Blueprint.
"""

from flask import Blueprint, jsonify, request, render_template
from typing import Any, Dict, List

from . import spellchecker_logic as logic
from . import database_manager
from . import __version__
from .database import get_db_connection
from .data_loader import calculate_and_cache_word_counts

# --- SERVER-SIDE VALIDATION CONSTANTS ---
MAX_SUGGESTION_LIMIT = 10
MAX_LEVENSHTEIN_DISTANCE = 3
DEFAULT_SUGGESTION_LIMIT = 5
DEFAULT_LEVENSHTEIN_DISTANCE = 2

# Create a Blueprint
api_blueprint = Blueprint('api', __name__)

# This context processor makes the nav_links list available to all templates
# rendered by this blueprint.
@api_blueprint.context_processor
def inject_nav_links():
    """Injects navigation links into the context of all templates."""
    nav_links = [
        {'endpoint': 'api.requested_words', 'text': 'وشە داواکراوەکان'}
    ]
    return dict(nav_links=nav_links, app_version=__version__)
    
# --- TEMPLATE-RENDERING VIEWS ---
@api_blueprint.route('/')
def index():
    """Renders the main spellchecker page with the initial word count."""
    # Pass the initial word count to the template for immediate display.
    total_words = len(logic.linguistic_data.get('suggestion_dictionary', []))
    return render_template('index.html', total_words=total_words)

@api_blueprint.route('/requested_words')
def requested_words():
    """Renders the page that displays user-requested words for review."""
    return render_template('requested_words.html')

# --- API ENDPOINTS ---
@api_blueprint.route('/api/check_text_block', methods=['POST'])
def check_text_block():
    """Receives a block of text and returns a list of problematic words."""
    text = request.get_json().get('text', '')
    problematic_words: List[Dict[str, Any]] = logic.check_text_block(text)
    return jsonify(problematic_words)

# --- Add a new endpoint to provide the live word count ---
@api_blueprint.route('/api/get_word_counts', methods=['GET'])
def get_word_counts():
    """Provides word counts from a cache. Calculates on first call."""
    # This check correctly handles cases where the key exists but is None.
    if logic.linguistic_data.get('word_counts') is None:
        calculate_and_cache_word_counts(logic.linguistic_data)
 
    # Return the cached data.
    return jsonify(logic.linguistic_data['word_counts'])


@api_blueprint.route('/api/get_suggestions', methods=['GET'])
def get_suggestions():
    """Provides spelling suggestions for a given word, enforcing server-side limits."""
    word = request.args.get('word')
    if not word:
        return jsonify({"error": "No word provided"}), 400
    
    # Gracefully handle and validate user input
    try:
        # Get user-provided values, falling back to defaults if they are not integers.
        user_limit = int(request.args.get('limit', DEFAULT_SUGGESTION_LIMIT))
        user_distance = int(request.args.get('distance', DEFAULT_LEVENSHTEIN_DISTANCE))
    except (ValueError, TypeError):
        # If the user provides non-numeric input (e.g., ?limit=abc), use defaults.
        user_limit = DEFAULT_SUGGESTION_LIMIT
        user_distance = DEFAULT_LEVENSHTEIN_DISTANCE

    # Clamp the values to the allowed server-side range
    limit = max(1, min(user_limit, MAX_SUGGESTION_LIMIT))
    distance = max(1, min(user_distance, MAX_LEVENSHTEIN_DISTANCE))
    
    suggestions = logic.get_combined_suggestions(word, limit, distance)
    
    # This is the crucial part that sends the authoritative data to the client
    return jsonify({
        "word": word, 
        "suggestions": suggestions,
        "limit_used": limit,
        "distance_used": distance
    })

@api_blueprint.route('/api/request_new_word', methods=['POST'])
def request_new_word():
    """Allows a logged-in user to request that a new word be added to the dictionary."""
    data = request.get_json()
    # Accept the anonymous hash from the client.
    word, user_hash = data.get('word'), data.get('user_hash')

    if not all([word, user_hash]):
        return jsonify({"status": "error", "message": "Missing 'word' or 'user_hash'"}), 400
    
    with get_db_connection() as db_conn:
        # Pass the hash to the database manager.
        result = database_manager.add_new_word_request(word, user_hash, db_conn)
        
    return jsonify(result)

@api_blueprint.route('/api/get_requested_words', methods=['GET'])
def get_requested_words():
    """Returns the complete list of user-requested words for the review page."""
    with get_db_connection() as db_conn:
        review_list = database_manager.get_all_requested_words(db_conn)
    return jsonify(review_list)

@api_blueprint.route('/api/version', methods=['GET'])
def get_version():
    """Returns the current version of the webservice."""
    return jsonify({"version": __version__})