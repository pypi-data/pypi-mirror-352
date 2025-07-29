#!/bin/bash

# ----------------------------
# Git Setup and First Push
# ----------------------------

echo "🔧 Initializing git and setting remote..."
git init
git remote add origin https://github.com/rperumal3000/DeliverFreshWhatsAppOrder

# ----------------------------
# Stage and Commit Changes
# ----------------------------

echo "📦 Staging and committing project files..."
git add .
git commit -m "Initial commit with project files"

# ----------------------------
# Push to GitHub
# ----------------------------

echo "🚀 Pushing to GitHub..."
git push -u origin main

# ----------------------------
# Pull if needed (to avoid non-fast-forward errors)
# ----------------------------

echo "🔄 Optional: Pull remote changes to sync if necessary..."
# git pull --rebase origin main

# ----------------------------
# Deploy Documentation with mike
# ----------------------------

echo "📚 Deploying documentation to gh-pages..."
mike deploy 0.1 latest --push --update-aliases --remote origin --allow-empty

# ----------------------------
# Remove unwanted Jupyter checkpoint folders
# ----------------------------

echo "🧹 Cleaning up .ipynb_checkpoints folders..."
rm -rf **/.ipynb_checkpoints
echo "**/.ipynb_checkpoints/" >> .gitignore
git add .gitignore
git rm -r --cached hi/hi/.ipynb_checkpoints 2>/dev/null
git commit -m "Remove .ipynb_checkpoints and add to .gitignore"
git push origin main

# ----------------------------
# Verify remote
# ----------------------------

echo "✅ Verifying remote settings..."
git remote -v

echo "✅ Done."
