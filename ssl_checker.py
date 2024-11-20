import socket
import ssl
from datetime import datetime
import requests
import os
import sys

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
    except socket.gaierror:
        log_error(f"Could not resolve domain: {domain}")
    except ssl.SSLError as e:
        log_error(f"SSL error for {domain}: {e}")
    except socket.timeout:
        log_error(f"Connection to {domain} timed out")
    except Exception as e:
        log_error(f"Error checking {domain}: {e}")
    return None

def send_notification(message):
    try:
        requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": "SSL Certificate Alert"}
        )
    except requests.RequestException as e:
        log_error(f"Failed to send notification: {e}")

def log_error(message):
    """Log errors and print them to standard output."""
    print(f"[ERROR] {message}", file=sys.stderr)

if __name__ == "__main__":
    errors = []
    for website in WEBSITES:
        if website.strip():
            result = check_ssl_certificate(website.strip(), WARNING_DAYS)
            if result:
                print(result)
            else:
                errors.append(website)

    if errors:
        print(f"Completed with errors for: {', '.join(errors)}", file=sys.stderr)

    # Exit with non-zero code if there are errors
    if errors:
        sys.exit(1)
