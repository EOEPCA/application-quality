FROM python:3.13.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y gcc libpq-dev postgresql-client redis-server supervisor curl jq \
    && curl -fSLo /usr/local/bin/kubectl https://dl.k8s.io/release/$(curl -sL https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && curl -fSLo /usr/local/bin/vcluster https://github.com/loft-sh/vcluster/releases/download/v0.24.1/vcluster-linux-amd64 \
    && chmod +x /usr/local/bin/vcluster \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 6379

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
