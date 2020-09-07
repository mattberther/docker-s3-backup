FROM python:3.8.5-alpine

RUN pip install boto
ADD app.py /app.py

CMD [ "python", "/app.py"]
