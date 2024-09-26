import logging
from flask import Flask, request, abort
import hmac
import hashlib
import subprocess

app = Flask(__name__)
SECRET = b'your_webhook_secret'  # Use bytes; replace with your actual secret

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify the request signature
    logging.info("Received a request on /webhook")
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        logging.error("Error: No signature found in the request headers.")
        abort(403)
    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        logging.error(f"Error: Unsupported SHA type {sha_name}.")
        abort(501)
    
    mac = hmac.new(SECRET, msg=request.data, digestmod='sha1')
    if not hmac.compare_digest(mac.hexdigest(), signature):
        logging.error("Error: Signature mismatch.")
        abort(403)
    
    # Pull the latest code
    logging.info("Attempting to pull the latest code...")
    git_pull = subprocess.run(
        ['/usr/bin/git', '-C', '/home/ubuntu/smartqna-be', 'pull'],
        capture_output=True, text=True
    )
    logging.info(f"Git Pull Output:\n{git_pull.stdout}")
    if git_pull.returncode != 0:
        logging.error(f"Error during git pull: {git_pull.stderr}")
        abort(500)

    # Restart the application
    logging.info("Attempting to restart the Gunicorn service...")
    restart_service = subprocess.run(
    ['sudo', '/bin/systemctl', 'restart', 'gunicorn'],
    capture_output=True, text=True
    )
    logging.info(f"Service Restart Output:\n{restart_service.stdout}")
    if restart_service.returncode != 0:
        logging.error(f"Error restarting Gunicorn service: {restart_service.stderr}")
        abort(500)

    logging.info("Webhook executed successfully.")
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
