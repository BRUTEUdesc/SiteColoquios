# syntax=docker/dockerfile:1

FROM python:3.11.3

WORKDIR /SiteColoquios

COPY requirements.txt requirements.txt
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

COPY . .

VOLUME [ "/SiteColoquios/app" ]

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:create_app()" ]
