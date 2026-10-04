FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces always expects port 7860
EXPOSE 7860
ENV PORT=7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]