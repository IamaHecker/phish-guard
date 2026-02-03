from pyngrok import ngrok
import time
import sys

# SIGN UP at https://dashboard.ngrok.com/get-started/your-authtoken
# AND PASTE YOUR TOKEN BELOW:
# Kill any existing ngrok processes to avoid "already online" errors
ngrok.kill()

# Set your auth token properly as a string
ngrok.set_auth_token("38en1nXIzKA6DrMkD2RDsaVFRyo_6tFryW2BfEKFgN9vz9Yny") 

try:
    # Open a HTTP tunnel on the default port 5000
    public_url = ngrok.connect(5000).public_url
    print(f"NGROK_URL: {public_url}")
    sys.stdout.flush()

    # Keep the process alive
    while True:
        time.sleep(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
