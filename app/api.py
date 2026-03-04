"""API Module"""

import os
import logging
from flask import Flask, jsonify
from flasgger import Swagger
from cifraclub import CifraClub, _cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Initialize Flasgger for OpenAPI / Swagger UI
swagger = Swagger(app, template={
    "info": {
        "title": "Cifra Club API",
        "description": (
            "API wrapper for Cifra Club chords and metadata. "
            "Uses a persistent Selenium session and in-memory caching to minimize response time."
        ),
        "version": "1.1.0"
    }
})

@app.route('/')
def home():
    """Home route
    ---
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            api:
              type: string
              example: Cifra Club API
    """
    return jsonify({'api': 'Cifra Club API', 'docs': '/apidocs', 'cache_size': len(_cache)}), 200

@app.route('/artists/<artist>/songs/<song>')
def get_cifra(artist, song):
    """Get cifra by artist and song
    ---
    parameters:
      - in: path
        name: artist
        type: string
        required: true
        description: Artist slug from CifraClub URL (e.g. coldplay)
      - in: path
        name: song
        type: string
        required: true
        description: Song slug from CifraClub URL (e.g. the-scientist)
    responses:
      200:
        description: Returns the song chords and metadata. Cached after first scrape.
      404:
        description: Song or artist not found on CifraClub
      500:
        description: Internal server error (e.g. Selenium failed)
    """
    try:
        cifrablub = CifraClub()
        result = cifrablub.cifra(artist, song)
        cached = f"{artist.lower()}::{song.lower()}" in _cache
        return jsonify({**result, '_cached': cached}), 200
    except ValueError as e:
        logger.error(f"Scraping error: {str(e)}")
        return jsonify({'error': 'Song or artist not found or could not be parsed.', 'details': str(e)}), 404
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return jsonify({'error': 'Internal server error.', 'details': str(e)}), 500

@app.route('/cache/status')
def cache_status():
    """View the current in-memory cache
    ---
    responses:
      200:
        description: Cache content
    """
    return jsonify({'count': len(_cache), 'keys': list(_cache.keys())}), 200

@app.route('/cache/clear', methods=['POST'])
def cache_clear():
    """Clear the in-memory cache
    ---
    responses:
      200:
        description: Cache cleared
    """
    cleared = len(_cache)
    _cache.clear()
    return jsonify({'cleared': cleared}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT', '3000'), debug=True)

