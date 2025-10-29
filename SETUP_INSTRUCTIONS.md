# ClarifyAI - Setup Instructions

## Overview
ClarifyAI is an intelligent document assistant powered by Gemini AI that allows users to:
- **Chat with PDF**: Upload PDF documents and ask questions about their content
- **Ask AI**: Get intelligent answers to any general questions

## Prerequisites
- Node.js (v16 or higher)
- Python 3.11+
- MongoDB (local or cloud instance)
- Gemini API Key from Google

## Local Setup Instructions

### 1. Clone or Extract the Project
```bash
# Extract the zip file and navigate to the project directory
cd clarifyai
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables
Edit the `backend/.env` file and add your Gemini API key:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="clarifyai_db"
CORS_ORIGINS="*"
JWT_SECRET="clarifyai-secret-key-change-in-production-12345"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

**How to get Gemini API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or use an existing one
4. Copy the key (starts with "AIza...")

#### Start Backend Server
```bash
# From backend directory
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The backend will be running at: `http://localhost:8001`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd ../frontend
yarn install
# or
npm install
```

#### Configure Frontend Environment
Edit the `frontend/.env` file:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

#### Start Frontend Server
```bash
# From frontend directory
yarn start
# or
npm start
```

The frontend will be running at: `http://localhost:3000`

### 4. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB locally and start the service
mongod --dbpath /path/to/data/directory
```

**Option B: MongoDB Atlas (Cloud)**
1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster
3. Get your connection string
4. Update `MONGO_URL` in `backend/.env`

## Usage

### 1. Create an Account
- Open `http://localhost:3000` in your browser
- Click on "Register" tab
- Enter username, email, and password
- Click "Create Account"

### 2. Use Chat with PDF
- After login, you'll see the dashboard
- Click on "Chat with PDF" tab
- Upload a PDF document
- Ask questions about the PDF content
- Get AI-powered answers based on the document

### 3. Use Ask AI
- Click on "Ask AI" tab
- Enter any question
- Get intelligent answers from Gemini AI

### 4. Logout
- Click the "Logout" button in the top-right corner

## Project Structure

```
clarifyai/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Global styles
│   │   ├── pages/
│   │   │   ├── Auth.jsx      # Login/Register page
│   │   │   └── Dashboard.jsx # Main dashboard
│   │   └── components/ui/    # Shadcn UI components
│   ├── package.json      # Node dependencies
│   └── .env             # Frontend environment variables
│
└── SETUP_INSTRUCTIONS.md # This file
```

## Features

### Authentication
- JWT-based authentication
- Secure password hashing with bcrypt
- Token-based session management

### Chat with PDF
- Upload PDF documents (temporary storage)
- Extract text from PDF automatically
- AI understands entire PDF context
- Fresh chat session for each upload

### Ask AI
- General-purpose AI assistant
- Powered by Gemini 2.5 Flash
- Fast and accurate responses

### UI/UX
- Professional tech design
- Responsive layout
- Beautiful gradient backgrounds
- Smooth animations and transitions
- Toast notifications for user feedback

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT (PyJWT + bcrypt)
- **PDF Processing**: PyPDF2
- **AI Integration**: Google Gemini 2.5 Flash via emergentintegrations

### Frontend
- **Framework**: React 19
- **UI Library**: Shadcn UI (Radix UI components)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Notifications**: Sonner

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Sign in

### AI Features
- `POST /api/ask-ai` - Ask general questions (requires authentication)
- `POST /api/chat-pdf` - Upload PDF and ask questions (requires authentication)

### Health Check
- `GET /api/` - Check if API is running

## Troubleshooting

### Backend won't start
- Check if MongoDB is running
- Verify all environment variables are set
- Ensure port 8001 is not already in use

### Frontend won't start
- Clear node_modules and reinstall: `rm -rf node_modules && yarn install`
- Check if port 3000 is available
- Verify REACT_APP_BACKEND_URL is correct

### AI not responding
- Verify your Gemini API key is correct
- Check backend logs for errors
- Ensure you have internet connectivity

### PDF upload fails
- Verify file is a valid PDF
- Check file size (large files may take longer)
- Ensure backend has proper permissions

## Security Notes

### For Production Deployment:
1. Change `JWT_SECRET` to a strong random string
2. Use environment-specific MongoDB credentials
3. Configure proper CORS origins
4. Use HTTPS for all connections
5. Implement rate limiting
6. Add input validation and sanitization
7. Set up proper logging and monitoring

## Support

For issues or questions:
- Check the troubleshooting section above
- Review backend logs: Check console output
- Review frontend logs: Open browser developer console (F12)

## License

This project is provided as-is for educational and commercial use.

---

**Built with Emergent AI** 🚀
