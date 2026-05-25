# DSPRO2 - The Virtual Coach
Data Science Projekt II

## Prerequisites
To run this project, you must have Docker installed on your machine or server: 

[Get Docker](https://docs.docker.com/get-started/get-docker/)

---

## Local Development

For local testing and development, you can spin up the application using the development configuration. 

```bash
docker compose -f docker-compose.dev.yaml up -d --build
```

Access the web application at http://localhost.

---

## Production Deployment

Because this application utilizes real-time motion tracking via the user's webcam, **modern web browsers strictly require a secure HTTPS connection** to grant camera permissions. 

To deploy this in production (e.g., on an AWS EC2 instance), you must set up a domain and SSL certificates. Our setup handles the SSL automatically via Caddy. If you do not have a custom domain name, you can use a free wildcard DNS service like [nip.io](https://nip.io).

### 1. Configure Your Domain
Rename the `.env.example` file to `.env` (or simply copy its contents into a newly created `.env` file). Open the `.env` file and define your `DOMAIN`. 

### 2. Start the Production Server
Run the production configuration. Caddy will read your `.env` file, bind to your domain, and automatically provision HTTPS certificates.

```bash
docker compose -f docker-compose.prod.yaml up -d --build
```

---

## Stopping the Application

To stop the running containers in either environment, execute:

```bash
docker compose -f docker-compose.dev.yaml down
# OR
docker compose -f docker-compose.prod.yaml down
```