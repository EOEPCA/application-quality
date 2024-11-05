FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && \
	apt-get install -y postgresql-client libpq-dev gcc && \
	rm -rf /var/lib/apt/lists/* && \
	pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV DJANGO_SETTINGS_MODULE=application_quality.settings \
	PYTHONUNBUFFERED=1

# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "application_quality.wsgi:application"]
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]