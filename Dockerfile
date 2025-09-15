FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Copy requirements and install
# System dependencies for scientific stack (numpy/scipy/cvxpy) and tools
RRUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    git \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Optional: Load env vars if using python-dotenv in app
RUN true

# Default command runs Streamlit bound to $PORT (Render injects $PORT)
EXPOSE 8501
ENV PORT=8501
CMD ["sh", "-lc", "streamlit run streamlit_app.py --server.port ${PORT} --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false --browser.gatherUsageStats false"]
