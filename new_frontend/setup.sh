#!/bin/bash
# filepath: /home/atom/Coding/Projects/Pentathon_Appathon/new_frontend/setup.sh

# Create necessary directories
mkdir -p data
mkdir -p templates
mkdir -p static/css
mkdir -p static/js

# Install required Python dependencies
pip install flask werkzeug

# Copy necessary files from existing projects
echo "Setting up integration with Human_built_flask..."
cp -r ../Human_built_flask/populate_database.py ./
cp -r ../Human_built_flask/query_data.py ./

echo "Setting up environment completed! You can now run the application with:"
echo "python app.py"
chmod +x setup.sh