# 1. Base image
FROM python:3.10-slim

# 2. System deps for video/audio and clean up
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 3. Copy and install Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your app code
COPY . .

# 5. Expose your port
EXPOSE 8080

# 6. Launch with Gunicorn for better concurrency
#    Assumes your Flask app object is called `app` in `app.py`
CMD ["gunicorn","-b","0.0.0.0:8080","app:app","--workers","1","--timeout","300"]

