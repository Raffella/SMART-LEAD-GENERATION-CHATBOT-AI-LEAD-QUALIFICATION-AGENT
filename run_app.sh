#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting AI Lead Qualification System Setup & Run...${NC}"

# Backend Setup & Run
echo -e "${GREEN}>>> Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing backend requirements..."
pip install -r requirements.txt

# Start Backend in background
echo -e "${GREEN}>>> Starting Backend Server on Port 8002...${NC}"
# Use standard environment variables from .env file that we created
uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
BACKEND_PID=$!

cd ..

# Frontend Setup & Run
echo -e "${GREEN}>>> Setting up Frontend...${NC}"
cd frontend

echo "Installing frontend dependencies..."
npm install

echo -e "${GREEN}>>> Starting Frontend Server...${NC}"
# Export VITE_BACKEND_URL for this process
export VITE_BACKEND_URL=http://localhost:8002
npm run dev

# Trap to kill backend when script exits
trap "kill $BACKEND_PID" EXIT
