from flask import Flask, jsonify, request, render_template
import requests
from typing import Dict, Any, Union
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# URL of our books service
# BOOKS_API_URL = "http://books-api-one.f9fxbdgdfhdtcpaj.uksouth.azurecontainer.io:5001"


BOOKS_API_URL = "http://books-api:5001"



@app.route('/')
def home():
    """Serve the search form"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handle book search form submission"""
    author = request.args.get('author')
    min_year = request.args.get('min_year')
    max_year = request.args.get('max_year')
    
    logger.debug(f"Search parameters received: author={author}, min_year={min_year}, max_year={max_year}")
    
    try:
        # Build query parameters
        params = {}
        if min_year:
            params['min_year'] = min_year
        if max_year:
            params['max_year'] = max_year
        if author:
            params['author'] = author
            
        logger.debug(f"Making request to {BOOKS_API_URL}/books with params: {params}")
        
        # Make request to books service
        response = requests.get(f"{BOOKS_API_URL}/books", params=params)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        
        if response.status_code == 200:
            books = response.json()['books']
            return render_template('index.html', books=books)
        else:
            return render_template('index.html', error=f'Failed to retrieve books: {response.status_code}')
            
    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return render_template('index.html', error=f'Service unavailable: {str(e)}')

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

@app.route('/books')
def get_filtered_books() -> Union[Dict[str, Any], tuple[Dict[str, Any], int]]:
    """Retrieve books with optional filters"""
    # Get filter parameters from request
    min_year = request.args.get('min_year')
    max_year = request.args.get('max_year')
    author = request.args.get('author')
    
    try:
        # Build query parameters
        params = {}
        if min_year:
            params['min_year'] = min_year
        if max_year:
            params['max_year'] = max_year
        if author:
            params['author'] = author
            
        # Make request to books service with filters
        response = requests.get(f"{BOOKS_API_URL}/books", params=params)
        
        if response.status_code == 200:
            books_data = response.json()['books']
            return jsonify({
                'message': 'Successfully retrieved filtered books',
                'count': len(books_data),
                'books': books_data,
                'filters_applied': {k: v for k, v in params.items() if v is not None}
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