FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use gunicorn for fast startup + consistent production behavior.
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "2", "--threads", "4"]

