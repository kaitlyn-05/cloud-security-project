
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Study-Room-Site-main/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY Study-Room-Site-main/ ./

EXPOSE 5000

CMD ["python", "app.py"]
