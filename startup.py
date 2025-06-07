import os
from app.app import app

# Use the imported Flask application instance
# No need to create it again since we're importing it directly

if __name__ == "__main__":
    # Get port from environment variable (Azure sets this)
    port = int(os.environ.get('PORT', 8000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Never run debug in production
    ) 