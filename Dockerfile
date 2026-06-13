FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY api/ ./api/
COPY agent/ ./agent/
COPY config/ ./config/
COPY database/ ./database/
COPY memory/ ./memory/
COPY pipelines/ ./pipelines/
COPY tools/ ./tools/
COPY main.py .

EXPOSE 8000

CMD ["python", "main.py"]