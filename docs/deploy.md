# Deployment Guide

This guide outlines the process for deploying updates to the UDESC's Maratona server for our Python web server application.

## Updating the Server

Here are the steps to deploy new changes to the UDESC server:

1. **Secure Shell (SSH) into the server:**

   If you're unsure how to do this, please reach out to a member of the [BRUTE](https://t.me/BRUTEudesc) team for guidance.

2. **Switch to superuser (sudo) mode:**

   You can do this by running the following command:
   ```bash
   sudo su
   ```
   Please note that the password required here is the same as the one used for logging in.

3. **Navigate to the project folder:**

   Use the following command to move into the project's directory:
   ```bash
   cd /var/www/coloquios/SiteColoquios
   ```

4. **Fetch the latest changes from the repository:**

   This can be achieved by running:
   ```bash
   git pull
   ```

5. **Restart the server:**

   Utilize the script to update the web server with this command:
   ```bash
   ./scripts/update_web_server.sh
   ```

## Scripts

The `scripts` directory houses several useful scripts for deployment, including:

- **initial_deploy.sh:** This script sets up the database and web server for the first time. Ensure you populate the .env file before running this script. 
  
- **update_web_server.sh:** Use this script after fetching the latest changes from the repository. This will ensure the web server is updated accordingly.

- **stop_and_clean.sh:** This script halts the database and web server, and subsequently destroys the containers. However, it retains the database data, allowing for a restart without data loss. Use the `initial_deploy.sh` script to restart the server.

## Containerization and Configuration

This application is containerized using Docker, with several Docker Compose files, each serving a different purpose:

- **Dockerfile:** Contains instructions for building the web server container.

- **docker-compose.yml:** The main Docker Compose file defining the database service.

- **docker-compose.override.yml:** Used exclusively for development, this file exposes the database port to the host machine.

- **docker-compose.prod.yml:** Specifically used for production, this file defines the web server service and links it to the database. The web server is exposed on port 8000.

The database and web server are deployed using Docker Compose, and the data is stored in the `db/data` folder. The web server employs Gunicorn to serve the application and is exposed on port 8000.

Please remember that deploying the services in a development environment is as simple as running `docker-compose up -d`. However, in a production environment, you need to use the appropriate scripts located in the `scripts` directory to start and stop the services.

## Apache2 Configuration

The UDESC server uses Apache2 to serve the website. The configuration file can be found at `/etc/apache2/sites-available/coloquios.conf`. 

Here's the configuration file content:

```apache
<VirtualHost *:80>
    ServerName brute.joinville.udesc.br
    ProxyPass /coloquios http://localhost:8000/coloquios
    ProxyPassReverse /coloquios http://localhost:8000/coloquios
</VirtualHost>
```

This configuration redirects all requests to `brute.joinville.udesc.br/coloquios` to the web server running on port 8000. The proxy module must be enabled for this configuration to work. While this should suffice for this project, if you need to modify the configuration, you can edit this file. After making changes, restart the Apache2 service with this command:

```bash
sudo service apache2 restart
```

## Environment Variables

This application utilizes a `.env` file to manage environment variables. Ensure you populate this file correctly before running any scripts that rely on it.

When handling the `.env` file or any other sensitive data, make sure to follow best security practices to prevent data breaches. Avoid exposing confidential information and always verify the secure transmission of data.

## Server and Database Management

The application's web server is exposed on port 8000 and uses Gunicorn as the WSGI HTTP server to serve the application. The database, on the other hand, is managed using Docker Compose, with all data stored in the `db/data` folder.
If the database is empty, create the necessary tables via the following commands:
  ```bash
  # Enter the web server container
  docker exec -it sitecoloquios-web-1 bash
  # Create the database
  flask db-create
  # Initialize the database
  flask db-init
  ```

## Contact Information

For any issues, please reach out to a member of the [BRUTE](https://t.me/BRUTEudesc) team for assistance.

Remember, while this guide aims to provide comprehensive instructions, unforeseen issues may arise during the deployment process. When in doubt, do not hesitate to seek help.
