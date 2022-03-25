FROM python:3.8-slim
LABEL maintainer="Jonny Le <jonny.le@computacenter.com>"

RUN apt-get update && apt-get install -y curl \
	&& rm -rf /var/lib/apt/lists/*

# Get Docker CLI
COPY --from=docker:20.10 /usr/local/bin/docker /usr/local/bin/

# Get docker-compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
	&& chmod +x /usr/local/bin/docker-compose

WORKDIR /api

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY api .

EXPOSE 80

CMD [ "gunicorn", "main:app", "--workers", "4", "--worker-class", \
      "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80" ]
