Basic SSL certificate expiry date checker for personal home lab use. 
Not recommended for serious use.

``` yml
services:
  ssl-checker:
    image: ghcr.io/42crmo4/certchecker:v1.0.0
    container_name: ssl-checker
    environment:
      - NTFY_SERVER=https://ntfy.sh
      - NTFY_TOPIC=ssl-notifications
      - WARNING_DAYS=7
      - WEBSITES=google.com, wikipedia.org
      - CHECK_INTERVAL=86400  # Check every 24 hours
    restart: always
```