# Qimchi

Plotly based data visualization tool for xarray data. Optimized to work with the [qcutils](https://gitlab.com/squad-lab/qcutils) package. Qimchi expects the data to be `zarr` formatted xarray files, documentation for handling these files can be found [here](https://xarray.pydata.org/en/stable/io.html#zarr).

Full API documentation and more can be found [here](https://qimchi.squad-lab.org)
## Installation

Qimchi supports multiple installation methods, including Docker, `uv`, and `pip`. We **recommend using Docker**, as it provides a containerized environment that isolates Qimchi from your local system. This ensures a smooth setup with all required dependencies and avoids potential conflicts with other software.

This guide provides instructions for installing Qimchi using various methods. Choose the one that best suits your use case.



## Docker Installation

> [!tip]
> Recommended, scroll down for local installation instructions.

### Prerequisites

First, ensure Docker is installed on your system. You can find installation instructions on the [official Docker website](https://docs.docker.com/get-docker/).  

> [!important]
> Docker might require administrative privileges to be installed and run.

### Basic Setup

To get started quickly without domain configuration, use the following `compose.yaml` file:

```yaml
networks:
  squad:
    driver: bridge

services:
  qimchi:
    image: registry.gitlab.com/squad-lab/qimchi:latest
    container_name: qimchi
    profiles: ["webdev"]
    restart: unless-stopped
    ports:
      - 80:80
    volumes:
      - ./qimchi/data:/root/.qimchi/
      - /your/data/:/data/
    networks:
      - squad
```

Environment variables can be provided via a `.env` file:

```
NUM_WORKERS=10
```

This setup exposes Qimchi on `localhost:80`.



### Advanced Setup (with Cloudflare Domain + HTTPS)

For production deployments with HTTPS and domain support (e.g., via Cloudflare), use the following `compose.yaml` configuration:

```yaml
networks:
  squad:
    driver: bridge

services:
  nginx:
    image: nginx:latest
    container_name: nginx
    profiles: ["webdev"]
    user: root
    restart: unless-stopped
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/letsencrypt:/etc/letsencrypt
      - ./nginx/html:/usr/share/nginx/html
    ports:
      - 80:80
      - 443:443
    networks:
      - squad

  certbot:
    image: certbot/dns-cloudflare
    container_name: certbot
    profiles: ["webdev"]
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./nginx/letsencrypt:/etc/letsencrypt
      - ./nginx/html:/usr/share/nginx/html
      - ./nginx/certbot-secrets:/certbot-secrets
    entrypoint: >
      /bin/sh -c '
      echo "dns_cloudflare_api_token=$$CLOUDFLARE_API_TOKEN" > /certbot-secrets/cloudflare.ini;
      chmod 600 /certbot-secrets/cloudflare.ini;
      trap exit TERM;
      while :; do certbot renew; sleep 12h & wait $${!}; done;
      '
    networks:
      - squad

  qimchi:
    image: registry.gitlab.com/squad-lab/qimchi:latest
    container_name: qimchi
    profiles: ["webdev"]
    restart: unless-stopped
    volumes:
      - ./qimchi/data:/root/.qimchi/
      - /your/data/:/data/
    networks:
      - squad
```

Environment file `.env` example:

```
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
NUM_WORKERS=10
```

Example NGINX configuration (`./nginx/conf.d/default.conf`):

```nginx
server {
    listen 80;
    server_name example.domain.org;

    # Redirect all HTTP traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name plot.domain.org;

    ssl_certificate /etc/letsencrypt/live/domain.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.org/privkey.pem;

    location / {
        proxy_pass http://qimchi:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

This setup uses Certbot with Cloudflare for automatic TLS certificate renewal. Be sure to replace `domain.org` and `plot.domain.org` with your actual domain names.

> [!note]
> The `CLOUDFLARE_API_TOKEN` environment variable is used to authenticate with Cloudflare's DNS API for domain verification.

## Local Installation
### With `uv`
Follow the official instructions from [Astral's website](https://astral.sh/uv/) to install `uv`. 
`uv` manages virtual environments and dependencies for you, making it easier to work 
with Python packages. For this project, we include the lock file which allows you to use 
the exact package versions we used to develop the package.

#### Measure and Plot

```shell

   uv init measurement_name
   cd measurement_name
   uv add qimchi
```

This method should automatically generate a virtual environment and install the package 
with all its dependencies. To add more packages to the current measurement/project, you 
can use the `uv add` command. For example, to add `qcodes` to the current project, run:

```shell
   uv add qcodes
```
`uv` automatically creates and manages the virtual environment for you.

#### Run Qimchi
To run Qimchi, use the following command:
```shell

   uv run -m qimchi
```
This command will start the Qimchi application, and you can access it in your web browser at `http://localhost`. If you can't. please check if you are allowed to have a hosted session at port 80. If not, you can run the application on a different port by using the `-p` option:

```shell

   uv run -m qimchi -p 8080
```

### With `pip`
#### Create and activate a virtual environment
On macOS or Linux:

```shell

   python3 -m venv .venv
   source .venv/bin/activate
```
On Windows:

```powershell

   python3 -m venv .venv
   .venv\Scripts\activate
```
#### Install the package
```shell

   pip install git+https://gitlab.com/squad-lab/qimchi.git
```
#### Run Qimchi
After activating the virtual environment, you can run the package with:

```shell

   python -m qimchi
```
This command will start the Qimchi application, and you can access it in your web browser at `http://localhost`. If you can't. please check if you are allowed to have a hosted session at port 80. If not, you can run the application on a different port by using the `-p` option:

```shell

   python -m qimchi -p 8080
```

## Development Installation
We strongly recommend using `uv` for development. You can clone and install the package locally with uv.
```shell

   git clone https://gitlab.com/squad-lab/qimchi.git
   cd qimchi
   uv add --dev .
```
This makes and installs qimchi in a virtual environment with all dependencies.

## Measurements
Measurement examples while using `qcutils` can be found in its own repository. Refer to [its repository](https://gitlab.com/squad-lab/qcutils) for more details.