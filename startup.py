import os
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (Azure sets this)
    port = int(os.environ.get('PORT', 8000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Never run debug in production
    ) 