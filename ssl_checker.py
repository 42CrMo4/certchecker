import socket
import ssl
from datetime import datetime, timezone
import requests
import os
import sys
import time
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get environment variables
NTFY_SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ssl-notifications")
WARNING_DAYS = int(os.getenv("WARNING_DAYS", 7))
WEBSITES = os.getenv("WEBSITES", "").split(',')
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))  # Default: 1 hour

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle termination signals to exit gracefully."""
    global running
    logging.info("Termination signal received. Exiting...")
    running = False

def check_ssl_certificate(domain, warning_days=7):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y GMT").replace(tzinfo=timezone.utc)
                days_left = (expiry_date - datetime.now(timezone.utc)).days

                if days_left <= warning_days:
                    message = f"SSL certificate for {domain} expires in {days_left} days!"
                    send_notification(message)
                return f"{domain}: {days_left} days left"
    except socket.gaierror:
        logging.error(f"Could not resolve domain: {domain}")
    except ssl.SSLError as e:
        logging.error(f"SSL error for {domain}: {e}")
    except socket.timeout:
        logging.error(f"Connection to {domain} timed out")
    except Exception as e:
        logging.error(f"Error checking {domain}: {e}")
    return None

def send_notification(message):
    try:
        requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": "SSL Certificate Alert"}
        )
        logging.info(f"Notification sent: {message}")
    except requests.RequestException as e:
        logging.error(f"Failed to send notification: {e}")

if __name__ == "__main__":
    # Register signal handlers for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while running:
        logging.info(f"Starting SSL checks for {len(WEBSITES)} website(s)...")
        errors = []
        for website in WEBSITES:
            if website.strip():
                result = check_ssl_certificate(website.strip(), WARNING_DAYS)
                if result:
                    logging.info(result)
                else:
                    errors.append(website)

        if errors:
            logging.error(f"Completed with errors for: {', '.join(errors)}")

        logging.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
        for _ in range(CHECK_INTERVAL):
            if not running:  # Exit the sleep early if a termination signal is received
                break
            time.sleep(1)
