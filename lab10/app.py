from flask import Flask, jsonify, abort
from typing import List, Dict, Any

app = Flask(__name__)

# Books data
books: List[Dict[str, Any]] = [
    {
        'id': 1,
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'publication_year': 1960,
        'genre': 'Southern Gothic'
    },
    {
        'id': 2,
        'title': '1984',
        'author': 'George Orwell',
        'publication_year': 1949,
        'genre': 'Dystopian Fiction'
    },
    {
        'id': 3,
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'publication_year': 1813,
        'genre': 'Romantic Novel'
    },
    {
        'id': 4,
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'publication_year': 1925,
        'genre': 'American Literature'
    },
    {
        'id': 5,
        'title': 'The Hunger Games',
        'author': 'Suzanne Collins',
        'publication_year': 2008,
        'genre': 'Young Adult Dystopian'
    }
]

@app.route('/')
def home() -> Dict[str, str]:
    """Root endpoint - API information"""
    return jsonify({
        'message': 'Welcome to the Books API',
        'available_endpoints': {
            'get_all_books': '/books',
            'get_book_by_id': '/books/<id>',
            'get_books_by_genre': '/genre/<genre>'
        }
    })

@app.route('/books', methods=['GET'])
def get_books() -> Dict[str, List]:
    """Return all books"""
    return jsonify({'books': books})

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id: int) -> Dict[str, Any]:
    """Return a specific book by ID"""
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        abort(404, description="Book not found")
    return jsonify({'book': book})

@app.route('/genre/<genre>', methods=['GET'])
def get_books_by_genre(genre: str) -> Dict[str, List]:
    """Return all books of a specific genre"""
    filtered_books = [book for book in books if book['genre'].lower() == genre.lower()]
    if not filtered_books:
        abort(404, description="No books found for this genre")
    return jsonify({'books': filtered_books})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
	
