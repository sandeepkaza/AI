FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Optional: Load env vars if using python-dotenv in app
RUN pip install python-dotenv

# Default command (adjust if different script is used)
CMD ["python", "main.py"]
