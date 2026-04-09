#!/usr/bin/env python
import os
import sys
import time
from pyngrok import ngrok
import subprocess
import threading

def start_django_server():
    """Start the Django development server"""
    os.chdir(r'c:\Users\VARUN\Desktop\kp\UVTech_VarunGaur')
    cmd = [sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000']
    return subprocess.Popen(cmd)

def main():
    print("🚀 Starting Neighbourhood Marketplace...")

    # Start Django server
    print("📡 Starting Django server...")
    server_process = start_django_server()

    # Wait a moment for server to start
    time.sleep(3)

    # Create ngrok tunnel
    print("🌐 Creating public tunnel...")
    try:
        # Set ngrok auth token if available (optional)
        # ngrok.set_auth_token("your_token_here")

        # Create HTTP tunnel
        public_url = ngrok.connect(8000, "http")
        print("✅ Server is now live!")
        print(f"🔗 Public URL: {public_url}")
        print("📱 You can access your website at the URL above")
        print("⚠️  Note: This is a temporary tunnel. Keep this script running.")

        # Keep the tunnel alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            ngrok.kill()
            server_process.terminate()

    except Exception as e:
        print(f"❌ Error creating tunnel: {e}")
        server_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()