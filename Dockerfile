# Dockerfile

# Start with an official, lightweight Python image
FROM python:3.10-slim

# Set environment variables for better Django/Python behavior inside Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python libraries listed in the requirements file
RUN pip install -r requirements.txt

# Copy our application's source code from the local 'src' folder
# into the container's '/app' directory
COPY ./src /app