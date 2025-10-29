# Where to Add Your Gemini API Key

## Location
Your Gemini API key should be added in the backend environment file:

**File Path**: `/backend/.env`

## How to Add It

1. Open the file: `/backend/.env`

2. Find the line that says:
   ```
   GEMINI_API_KEY=""
   ```

3. Replace it with your API key:
   ```
   GEMINI_API_KEY="AIzaSyDHFF12ZJZcx5YME7K9zv6Bd7_ps_g5NeU"
   ```
   *(Your actual API key)*

4. Save the file

5. Restart the backend server:
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

## How to Get a Gemini API Key

If you need a new API key:

1. Visit: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"** button
4. Copy the generated key (it starts with "AIza...")
5. Paste it in the `.env` file as shown above

## Important Notes

- ⚠️ Never share your API key publicly
- ⚠️ Don't commit the `.env` file with your key to Git
- ⚠️ Keep your API key secure and private
- The API key is already configured in your current deployment
- You only need to add it when running locally on your machine

## Current Configuration

Your API key is already set in the deployed version:
- It's configured in `/app/backend/.env`
- The backend is using Gemini 2.5 Flash model
- Both "Chat with PDF" and "Ask AI" features are working

## For Local Development

When you download and run the code locally:
1. Extract the zip file
2. Navigate to `backend/.env`
3. Add your Gemini API key as shown above
4. Follow the setup instructions in `SETUP_INSTRUCTIONS.md`
