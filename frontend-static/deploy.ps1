# FixBuddy Frontend Deployment Script
Write-Host "🚀 FixBuddy Frontend Deployment to Vercel" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

Write-Host "Step 1: Installing Vercel CLI..." -ForegroundColor Yellow
npm install -g vercel

Write-Host "Step 2: Please login to Vercel (browser will open)..." -ForegroundColor Yellow
vercel login

Write-Host "Step 3: Deploying to Vercel..." -ForegroundColor Yellow
vercel --prod

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Your website is now live on Vercel!" -ForegroundColor Green
Read-Host "Press Enter to exit"