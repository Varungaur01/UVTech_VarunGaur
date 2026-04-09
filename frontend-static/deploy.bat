@echo off
echo 🚀 FixBuddy Frontend Deployment to Vercel
echo ==========================================

echo Step 1: Installing Vercel CLI...
npm install -g vercel

echo.
echo Step 2: Please login to Vercel (browser will open)...
vercel login

echo.
echo Step 3: Deploying to Vercel...
vercel --prod

echo.
echo ✅ Deployment complete!
echo Your website is now live on Vercel!
pause