#!/usr/bin/env python3
"""
HushMCP Vercel Environment Setup Script
Helps you set up all required environment variables for Vercel deployment
"""

print("🔧 HushMCP Vercel Environment Variables Setup")
print("=" * 50)
print()

print("📋 Copy these environment variables to your Vercel Dashboard:")
print("   Go to: https://vercel.com/dashboard")
print("   Select your backend project → Settings → Environment Variables")
print()

env_vars = {
    "SECRET_KEY": "5cab39d53c7f4f8637eef643b892bc0695f55664d5c95f74c2415f2a9b12f02e",
    "VAULT_ENCRYPTION_KEY": "bd6e9162452ec69198a8d67e395f87a4dbed9b2e46feb4f7e0a0c0feedaa3d06", 
    "VAULT_MASTER_KEY": "f651f8fda8fc6cd4340cea7ac18f4d3bc579742f9116fa0b5449e59fde6055d3",
    "GEMINI_API_KEY": "AIzaSyCyTIMomAZ-EtebfSToII2gwLo8pInVXwY",
    "MAILJET_API_KEY": "cca56ed08f5272f813370d7fc5a34a24",
    "MAILJET_API_SECRET": "60fb43675233e2ac775f1c6cb8fe455c",
    "PINECONE_API_KEY": "pcsk_6vCMdb_3WH5y9VhN4oj9zcCyVTynYMMEM6p9peJad3dE3kauD3dD1Q6Mo5F3pWDtV5YXTT",
    "PINECONE_ENVIRONMENT": "3fe7cae0-f092-408c-98e1-c48f9303e809"
}

print("🔑 Environment Variables:")
print("-" * 50)
for key, value in env_vars.items():
    print(f"{key}={value}")

print()
print("🚀 After setting these in Vercel:")
print("1. Go to your backend project in Vercel")
print("2. Click 'Redeploy' or run 'vercel --prod' locally")
print("3. Test your frontend at: https://your-frontend-url.vercel.app")
print()
print("✅ Your HushMCP privacy-first AI system will be ready!")
