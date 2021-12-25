FROM python:3.8.5

WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir
COPY . .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000