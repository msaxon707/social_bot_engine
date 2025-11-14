# ---- Base Image ----
FROM python:3.11-slim

# ---- System Dependencies ----
# ffmpeg is mandatory for MoviePy to generate videos
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# ---- App Directory ----
WORKDIR /app

# ---- Install Python Dependencies ----
# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Force stable MoviePy version
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy Application Code ----
COPY . .

# ---- Default Run Command ----
# This runs your scheduling engine once per container exec.
CMD ["python", "run.py"]
