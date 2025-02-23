# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot script
COPY discord_bot.py .

# Command to run your bot
CMD ["python", "discord_bot.py"]

