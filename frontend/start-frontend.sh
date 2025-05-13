#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Frontend Setup Script${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}Node.js and npm detected${NC}"

# Install dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please check your package.json and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully${NC}"

# Test backend connection directly to make sure it's running
echo -e "${YELLOW}Testing backend connection...${NC}"

# Backend URL for direct testing (should match the Vite proxy target)
BACKEND_URL="http://127.0.0.1:5001/api/user"

# Test the connection
echo -e "${YELLOW}Attempting to connect to backend at: ${BACKEND_URL}${NC}"
curl -s --head --request GET ${BACKEND_URL} --max-time 5 > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Could not connect to backend at ${BACKEND_URL}. Make sure the backend is running.${NC}"
    
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}Backend connection successful${NC}"
fi

# Run linting and tests if available
if grep -q "\"lint\":" package.json; then
    echo -e "${YELLOW}Running linting...${NC}"
    npm run lint
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Linting failed. Do you want to continue? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}Linting passed${NC}"
    fi
fi

if grep -q "\"test\":" package.json; then
    echo -e "${YELLOW}Running tests...${NC}"
    npm test -- --watchAll=false
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Tests failed. Do you want to continue? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}Tests passed${NC}"
    fi
fi

# Start the frontend server using Vite dev command
echo -e "${YELLOW}Starting frontend development server...${NC}"
echo -e "${GREEN}The frontend will be available at http://localhost:5173${NC}"
echo -e "${GREEN}API requests will be proxied to http://127.0.0.1:5001${NC}"
npm run dev

# This line will only execute if the npm run dev command exits
echo -e "${RED}Frontend server has stopped${NC}"