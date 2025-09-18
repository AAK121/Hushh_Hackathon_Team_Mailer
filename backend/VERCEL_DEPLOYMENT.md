# Vercel Deployment for HushMCP Agent API

This directory contains the Vercel deployment configuration for the HushMCP Agent API server.

## Files Created for Vercel Deployment

- `vercel.json` - Vercel deployment configuration
- `index.py` - Entry point for Vercel serverless environment
- `.vercelignore` - Files to exclude from deployment

## Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from the backend directory**:
   ```bash
   cd backend
   vercel
   ```

4. **For production deployment**:
   ```bash
   vercel --prod
   ```

## Environment Variables Configuration

Before deploying, you need to configure the following environment variables in Vercel:

### Required Environment Variables:
- `GEMINI_API_KEY` - Google Gemini API key for AI operations
- `GOOGLE_API_KEY` - Google API key for calendar integration
- `MAILJET_API_KEY` - Mailjet API key for email sending
- `MAILJET_API_SECRET` - Mailjet API secret
- `SECRET_KEY` - Secret key for JWT token signing
- `VAULT_ENCRYPTION_KEY` - Key for encrypting vault data
- `SENDER_EMAIL` - Default sender email address

### Optional Environment Variables:
- `DATABASE_URL` - Database connection string (if using database)
- `PINECONE_API_KEY` - Pinecone API key for vector storage
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `REDIS_URL` - Redis connection URL

## Setting Environment Variables in Vercel

You can set environment variables through:

1. **Vercel Dashboard**:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add each variable with appropriate values

2. **Vercel CLI**:
   ```bash
   vercel env add GEMINI_API_KEY
   vercel env add GOOGLE_API_KEY
   # ... add other variables
   ```

## API Endpoints

Once deployed, your API will be available at `https://your-project.vercel.app` with the following endpoints:

- `/docs` - Interactive API documentation
- `/redoc` - Alternative API documentation
- `/agents/addtocalendar/` - AddToCalendar agent endpoints
- `/agents/mailerpanda/` - MailerPanda agent endpoints
- `/agents/chandufinance/` - ChanduFinance agent endpoints
- `/agents/relationship_memory/` - Relationship Memory agent endpoints
- `/agents/research/` - Research agent endpoints
- `/agents/chat/` - General chat agent endpoints

## Local Testing

To test the deployment configuration locally:

```bash
python index.py
```

This will start the server on `http://localhost:8000`

## Troubleshooting

1. **Import Errors**: Make sure all dependencies are listed in `requirements.txt`
2. **Module Not Found**: Check that the Python path is correctly configured
3. **Timeout Issues**: Adjust `maxDuration` in `vercel.json` if needed
4. **Environment Variables**: Verify all required environment variables are set in Vercel dashboard

## Notes

- The serverless environment has a 30-second timeout limit
- Large files and directories are excluded via `.vercelignore`
- The vault directory is excluded for security reasons
- Consider using external storage for large data files
