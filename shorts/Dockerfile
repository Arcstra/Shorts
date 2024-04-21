FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code/

COPY ./requirements.txt /code/

RUN pip install "setuptools<58.0.0" && pip install -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD [ "sh", "-c", "python manage.py makemigrations api && python manage.py migrate" ]
