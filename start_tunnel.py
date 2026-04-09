from pyngrok import ngrok
import time

# Start ngrok tunnel to port 8000
print("Starting ngrok tunnel...")
tunnel = ngrok.connect(8000, "http")
print(f"Public URL: {tunnel.public_url}")
print("Press Ctrl+C to stop the tunnel")

# Keep the tunnel alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping tunnel...")
    ngrok.disconnect(tunnel.public_url)
    ngrok.kill()