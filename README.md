# PRTG Test Drive

This Self-Service Test Drive API offers clients a quick and easy way to launch their own PRTG Test Drive instance. This API supports multiple containerized PRTG instances and fake devices, all isolated in their own network. It also features automated HTTPS using [Caddy](https://github.com/lucaslorentz/caddy-docker-proxy) as a reverse proxy.

## Table of Contents
* [The Details](#the-details)
* [Getting Started](#getting-started)
    * [Requirements](#requirements)
    * [Installation](#installation)
* [Usage](#usage)
* [TODOs](#todos)
* [Author](#author)
* [License](#license)

## The Details

Test Drive is a sandbox environment to freely explore and learn a part of the Expert Services experience. With this API, clients can start up their own instance in minutes with just a name and token. This automatically creates their own PRTG instance and fake devices, isolated on their own network. Using Caddy, the API returns a HTTPS link to the PRTG instance.

This API also demonstrates the advantage of using the [XSAutomate API](https://github.com/CC-Digital-Innovation/reconcile-snow-prtg) to import the devices from SNOW. It automatically creates the tree structure, add all the devices, and fill in the proper fields, e.g. location, IP address/hostname, SNOW link, etc.

## Getting Started

### Requirements

**XSAutoamte API**

This API requires a locally built, Windows version of the XSAutomate API.
1. Clone [XSAutomate API](https://github.com/CC-Digital-Innovation/reconcile-snow-prtg) project into root directory.
2. Decrypt `encrypted.ini` file or create and properly edit `config.ini` file.
3. Update Dockerfile:
```Dockerfile
FROM python:3.9.12-windowsservercore-1809

WORKDIR "C:/Program Files/api"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2", "--loop", "asyncio" ]
```

**Windows Server 2019 with Docker**

* Launching PRTG containers require a specific host runnning Docker. It is required to read lordmilko's [documents](https://github.com/lordmilko/PrtgDocker)!

**Docker Compose**

* Docker Compose is properly setup and installed.

**Wildcard DNS Record**

* When ready for production, point a wildcard DNS record to the host system's external IP address.

### Installation

Clone repo from GitHub:
```bash
git clone https://github.com/CC-Digital-Innovation/prtg-test-drive.git
```
* or download the [zip](https://github.com/CC-Digital-Innovation/prtg-test-drive/archive/refs/heads/main.zip)

## Usage

_The code snippets assume you are user in docker group which does not require sudo. If you are not, each command will require sudo prepended._

1. Create network for Caddy
```bash
docker network create caddy
```

2. For production ready API, set an environment variable of your domain name for the api:
```bash
API_DOMAIN=example.com
```
- If no environment variable is set, it will default to localhost.

3. Simply build and start containers:
```bash
docker-compose up -d --build
```
- `--build` flag is only necessary the first time or when new changes are made. Subsequent deployments do not require it.
 
4. API is accessible at api.\<domain-name\>, or api.localhost if not set.
 
## TODOs
* Remove need for users to create template device
* Use a different, fake device image that supports more sensors.

## Author
* Jonny Le <<jonny.le@computacenter.com>>

## License
MIT License

Copyright (c) 2021 Computacenter Digital Innovation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
