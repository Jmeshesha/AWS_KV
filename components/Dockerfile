FROM python:3.7-slim

WORKDIR /app

COPY . /app

RUN pip install -r Requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]