#!/bin/bash

# Automated deployment script
# This script will commit all changes and push to GitHub

echo "Starting automated deployment..."

# Add all changes
git add .

# Check if there are changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
    exit 0
fi

# Commit changes
git commit -m "Automated content update $(date)"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin master

echo "Deployment completed successfully!"
echo "Waiting for GitHub Pages build..."
