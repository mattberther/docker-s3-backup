FROM python:3.8.5-alpine
RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

RUN pip install -e .

CMD [ "s3_backup" ]
