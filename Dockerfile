FROM python:3.10-slim

ENV PYTHONBUFFERED=1

ADD ./requirements.txt /app/requirements.txt

ADD . /app 
WORKDIR /app

RUN apt update -y

RUN pip install --upgrade pip
RUN pip install django
RUN pip install djangorestframework
RUN pip install gunicorn
RUN pip install moviepy
RUN pip install requests

# RUN pip install -r /app/requirements.txt
# RUN python manage.py makemigrations 
# RUN python manage.py migrate
RUN python manage.py collectstatic


COPY entrypoint.sh /app/entrypoint.sh

EXPOSE 8000


ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", ":8000", "--timeout", "600", "--workers", "1", "chromeapi.wsgi:application"]