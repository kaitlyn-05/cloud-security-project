
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Linux libraries required by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY Study-Room-Site-main/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY Study-Room-Site-main/ ./

EXPOSE 5000

CMD ["python", "app.py"]
