# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Database Manager
Handles direct database interactions that occur during web requests,
such as writing new data or fetching dynamic lists.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Dict, List, Any
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

def add_new_word_request(word: str, user_hash: str, db_conn: Connection[DictCursor]) -> Dict[str, str]:
    """
    Adds a user's request for a new word to the database using an anonymous hash.
    It checks for duplicate requests from the same user for the same word.
    """
    # Use the client’s anonymous hash for defense-in-depth
    submission_hash = hashlib.sha256(f"{word}-{user_hash}".encode('utf-8')).hexdigest()
    cursor: DictCursor = db_conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM requested_words_log WHERE submission_hash = %s", (submission_hash,))
        if cursor.fetchone():
            return {"status": "success", "message": "پێشتر داواکاریت بۆ ئەم وشەیە ناردووە."}
        
        cursor.execute("INSERT INTO requested_words_log (submission_hash) VALUES (%s)", (submission_hash,))
        
        sql = """
            INSERT INTO requested_words (word, request_count, status, first_seen, last_updated) 
            VALUES (%s, 1, 'pending', %s, %s) 
            ON DUPLICATE KEY UPDATE request_count = request_count + 1, last_updated = %s
        """
        now = datetime.now()
        cursor.execute(sql, (word, now, now, now))
        db_conn.commit()
        
        return {"status": "success", "message": "داواکارییەکەت بە سەرکەوتوویی تۆمار کرا."}
    finally:
        cursor.close()

def get_all_requested_words(db_conn: Connection[DictCursor]) -> List[Dict[str, Any]]:
    """
    Fetches and formats the list of all user-suggested words from the database,
    ordered by status and requests count for easy review.
    """
    # A dictionary for translations
    status_translations = {
        'pending': 'ھەڵواسراو',
        'approved': 'پەسەندکراو',
        'rejected': 'ڕەتکرایەوە'
    }

    cursor: DictCursor = db_conn.cursor()
    try:
        query = """
            SELECT word, request_count, status, first_seen, last_updated 
            FROM requested_words 
            ORDER BY FIELD(status, 'pending', 'approved', 'rejected'), request_count DESC
        """
        cursor.execute(query)
        review_list = list(cursor.fetchall())
        
        for item in review_list:
            # Convert datetime objects to a JSON-serializable format (ISO string)
            item['first_seen'] = item['first_seen'].isoformat()
            item['last_updated'] = item['last_updated'].isoformat()
            
            # Add the translated status using the original 'status' value as a key
            # .get() is used safely in case there's an unexpected status value
            item['status_kurdish'] = status_translations.get(item['status'], item['status'])
            
        return review_list
    finally:
        cursor.close()
        