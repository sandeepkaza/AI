FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Copy requirements and install
# System dependencies for scientific stack (numpy/scipy/cvxpy) and tools
RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
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
RUN pip install python-dotenv && \
	chmod +x /app/start.sh

# Default command runs Streamlit bound to $PORT for Render
EXPOSE 8000
CMD ["/app/start.sh"]
