FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system deps (safe minimum)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Default command (both backend + UI)
CMD ["bash", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port 8000 & streamlit run frontend/dashboard.py --server.port 8501 --server.address 0.0.0.0"]
