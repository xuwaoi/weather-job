FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY weather_job.py .
CMD ["python", "weather_job.py"]
