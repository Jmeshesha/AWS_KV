FROM nogil/python

WORKDIR /app

COPY . /app

ENV TZ=America/New_York

RUN pip install -r Requirements.txt

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]