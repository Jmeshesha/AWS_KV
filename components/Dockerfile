FROM nogil/python

WORKDIR /app

COPY . /app

ENV TZ=America/New_York

RUN pip install -r Requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]