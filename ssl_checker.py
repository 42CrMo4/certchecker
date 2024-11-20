import socket
import ssl
from datetime import datetime, timedelta
import requests
import os

# Get environment variables
NTFY_SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ssl-notifications")
WARNING_DAYS = int(os.getenv("WARNING_DAYS", 7))
WEBSITES = os.getenv("WEBSITES", "").split(',')

def check_ssl_certificate(domain, warning_days=7):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y GMT")
                days_left = (expiry_date - datetime.utcnow()).days

                if days_left <= warning_days:
                    message = f"SSL certificate for {domain} expires in {days_left} days!"
                    send_notification(message)
                return f"{domain}: {days_left} days left"
    except Exception as e:
        message = f"Error checking {domain}: {e}"
        send_notification(message)
        return message

def send_notification(message):
    try:
        requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": "SSL Certificate Alert"}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

if __name__ == "__main__":
    for website in WEBSITES:
        if website.strip():
            print(check_ssl_certificate(website.strip(), WARNING_DAYS))
