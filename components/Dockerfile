FROM python:3.7-alpine

WORKDIR /app

COPY . /app

RUN pip install -r Requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]