# Use Python 3.11 as the base image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY ssl_checker.py .

# Install required Python libraries
RUN pip install requests

# Set default environment variables
ENV NTFY_SERVER=https://ntfy.sh \
    NTFY_TOPIC=ssl-notifications \
    WARNING_DAYS=7 \
    WEBSITES="example.com,anotherdomain.com"

# Run the script
CMD ["python", "-u", "ssl_checker.py"]

