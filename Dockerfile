# Use Python base 
FROM python:3.11-slim

# Set env var
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working dir
WORKDIR /app

# Install dependencies from file in root dir
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy proj
COPY . .

# Expose Flask port
EXPOSE 5000

# Run app
CMD ["python", "run.py"]
