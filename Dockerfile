FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP /app/app.py

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "-p", "5000"]
