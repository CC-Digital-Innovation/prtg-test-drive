FROM python:3.9.12-windowsservercore-1809
LABEL maintainer="Jonny Le <jonny.le@computacenter.com>"

# Get Docker CLI
COPY --from=docker:20.10.14-windowsservercore-1809 ["C:/Program Files/docker/docker.exe", "C:/Program Files/docker/"]

# Get docker-compose
RUN Invoke-WebRequest "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Windows-x86_64.exe" -UseBasicParsing -OutFile $Env:ProgramFiles\docker\docker-compose.exe

RUN setx /M PATH $($Env:PATH + ';C:/Program Files/docker')

WORKDIR "C:/Program Files/docker/api"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY api .

EXPOSE 80

# Gunicorn does not support Windows
# CMD [ "gunicorn", "main:app", "--workers", "4", "--worker-class", \
#       "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80" ]
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]
