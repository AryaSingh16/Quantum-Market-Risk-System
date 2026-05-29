FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create runtime directories
RUN mkdir -p data figures

EXPOSE 8000
EXPOSE 8501

CMD ["bash", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port 8000 & sleep 3 && streamlit run frontend/dashboard.py --server.port 8501 --server.address 0.0.0.0"]
