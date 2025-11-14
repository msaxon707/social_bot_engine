FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg for MoviePy
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
