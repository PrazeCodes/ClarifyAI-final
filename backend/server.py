from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from PyPDF2 import PdfReader
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 30

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user: User

class AskAIRequest(BaseModel):
    question: str

class ChatPDFRequest(BaseModel):
    question: str
    pdf_text: str

class AIResponse(BaseModel):
    answer: str

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password': 0})
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF text: {str(e)}")

async def call_gemini_api(prompt: str, system_message: str = "You are a helpful AI assistant.") -> str:
    """Call Gemini API using emergentintegrations"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        session_id = str(uuid.uuid4())
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("gemini", "gemini-1.5-flash")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logging.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# Auth Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({'email': user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email
    )
    
    user_dict = user.model_dump()
    user_dict['password'] = hash_password(user_data.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    token = create_jwt_token(user.id)
    return TokenResponse(token=token, user=user)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    # Convert to User model (exclude password)
    user_obj = User(
        id=user['id'],
        username=user['username'],
        email=user['email'],
        created_at=datetime.fromisoformat(user['created_at']) if isinstance(user['created_at'], str) else user['created_at']
    )
    
    token = create_jwt_token(user['id'])
    return TokenResponse(token=token, user=user_obj)

# AI Routes
@api_router.post("/ask-ai", response_model=AIResponse)
async def ask_ai(request: AskAIRequest, current_user: dict = Depends(get_current_user)):
    """General AI question answering"""
    answer = await call_gemini_api(
        prompt=request.question,
        system_message="You are ClarifyAI, a helpful and knowledgeable AI assistant. Provide clear, accurate, and helpful answers to user questions."
    )
    return AIResponse(answer=answer)

@api_router.post("/chat-pdf", response_model=AIResponse)
async def chat_with_pdf(
    question: str = Form(...),
    pdf_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Chat with uploaded PDF"""
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are allowed')
    
    # Read and extract text from PDF
    pdf_content = await pdf_file.read()
    pdf_text = extract_text_from_pdf(pdf_content)
    
    if not pdf_text:
        raise HTTPException(status_code=400, detail='Could not extract text from PDF')
    
    # Create prompt with PDF context
    prompt = f"""Based on the following PDF content, answer the user's question.

PDF Content:
{pdf_text}

User Question: {question}

Provide a clear and accurate answer based on the PDF content."""
    
    answer = await call_gemini_api(
        prompt=prompt,
        system_message="You are ClarifyAI, an AI assistant specialized in analyzing documents and answering questions based on provided content. Always base your answers on the document content."
    )
    
    return AIResponse(answer=answer)

@api_router.get("/")
async def root():
    return {"message": "ClarifyAI API is running"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()