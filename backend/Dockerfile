FROM python:slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
	&& apt-get install -y gcc libpq-dev postgresql-client redis-server supervisor \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 6379

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
