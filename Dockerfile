FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "/app/app.py"]
