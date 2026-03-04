"""API Module"""

import os
import logging
from flask import Flask, jsonify
from flasgger import Swagger
from cifraclub import CifraClub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Initialize Flasgger for OpenAPI / Swagger UI
swagger = Swagger(app, template={
    "info": {
        "title": "Cifra Club API",
        "description": "API wrapper for Cifra Club chords and metadata.",
        "version": "1.0.0"
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
    return jsonify({'api': 'Cifra Club API'}), 200

@app.route('/artists/<artist>/songs/<song>')
def get_cifra(artist, song):
    """Get cifra by artist and song
    ---
    parameters:
      - in: path
        name: artist
        type: string
        required: true
        description: The artist's name based on CifraClub URL structure (e.g. coldplay)
      - in: path
        name: song
        type: string
        required: true
        description: The song's name based on CifraClub URL structure (e.g. the-scientist)
    responses:
      200:
        description: Returns the song chords and metadata
      404:
        description: Song or artist not found
      500:
        description: Internal server error (e.g., Selenium scraping failed)
    """
    try:
        cifrablub = CifraClub()
        result = cifrablub.cifra(artist, song)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Scraping error: {str(e)}")
        # Assuming ValueError means it couldn't find the elements (404) 
        # or site structure changed. For now, treat parsing errors as 404 (Not Found).
        return jsonify({'error': 'Song or artist not found or could not be parsed.', 'details': str(e)}), 404
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return jsonify({'error': 'Internal server error while processing the request.', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT', '3000'), debug=True)
