from flask import Flask, jsonify, request
import requests
from typing import Dict, Any, Union

app = Flask(__name__)

# URL of our books service
BOOKS_API_URL = "http://books-api-one.f9fxbdgdfhdtcpaj.uksouth.azurecontainer.io:5001"

@app.route('/')
def home() -> Dict[str, str]:
    """Root endpoint with service information"""
    return jsonify({
        'message': 'Welcome to the Books Client Service',
        'endpoints': {
            'get_books_by_genre': '/books/genre?genre=<genre_name>',
            'get_newest_book': '/newest-book'
        }
    })

@app.route('/books/genre')
def get_books_by_genre() -> Union[Dict[str, Any], tuple[Dict[str, Any], int]]:
    """Retrieve books of a specific genre from the books service"""
    # Get genre from query parameter, default to None if not provided
    genre = request.args.get('genre')
    
    if not genre:
        return jsonify({
            'error': 'Genre parameter is required',
            'usage': '/books/genre?genre=<genre_name>'
        }), 400
    
    try:
        # Make request to books service
        response = requests.get(f"{BOOKS_API_URL}/genre/{genre}")
        
        if response.status_code == 200:
            books_data = response.json()['books']
            return jsonify({
                'message': f'Successfully retrieved books in genre: {genre}',
                'count': len(books_data),
                'books': books_data
            })
        elif response.status_code == 404:
            return jsonify({
                'message': f'No books found for genre: {genre}'
            }), 404
        else:
            return jsonify({
                'error': 'Failed to retrieve books',
                'status_code': response.status_code
            }), 500
            
    except requests.RequestException as e:
        return jsonify({
            'error': 'Service unavailable',
            'details': str(e)
        }), 503

@app.route('/newest-book')
def get_newest_book() -> Union[Dict[str, Any], tuple[Dict[str, Any], int]]:
    """Retrieve the most recently published book"""
    try:
        # Get all books
        response = requests.get(f"{BOOKS_API_URL}/books")
        
        if response.status_code == 200:
            # Extract all books and find the newest one
            books = response.json()['books']
            newest_book = max(books, key=lambda x: x['publication_year'])
            
            return jsonify({
                'message': 'Successfully retrieved newest book',
                'book': newest_book
            })
        else:
            return jsonify({
                'error': 'Failed to retrieve books',
                'status_code': response.status_code
            }), 500
            
    except requests.RequestException as e:
        return jsonify({
            'error': 'Service unavailable',
            'details': str(e)
        }), 503

if __name__ == '__main__':
    # Run on a different port than the books service
    app.run(host='0.0.0.0', port=5002)
