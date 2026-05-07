#!/bin/bash

# Setup script for eDNA Analysis System

echo "========================================="
echo "eDNA Analysis System - Setup"
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "✓ Python and Node.js found"

# Setup Frontend
echo ""
echo "Setting up frontend..."
npm install
cp .env.example .env
echo "✓ Frontend setup complete"

# Setup Backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/uploads data/results data/training ml_models logs

# Copy environment file
cp .env.example .env

echo "✓ Backend setup complete"

cd ..

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Download and train a model:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python scripts/quick_start_training.py"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   python app/main.py"
echo ""
echo "3. Start the frontend (in another terminal):"
echo "   npm run dev"
echo ""
echo "4. Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "========================================="
