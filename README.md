# Wedding Website API

This is the API for my wedding website.

## First Installation

Complete the below steps to run the project locally and allow running unit tests via Docker:

1. Ensure you have created a Docker Hub account, downloaded Docker Desktop and signed in to the Docker Desktop with your Docker Hub account details
2. Checkout develop branch
3. Add the `.env` file in the project's root directory
4. Add the `test_settings.py` file in the `WeddingWebsiteBackend` directory
5. Run `docker-compose -f ./docker-compose-local.yaml up -d` from the terminal
   1. The container will run in the background
   2. This may take a while to install for the first installation
6. Run `docker exec wedding-website-backend-db-1 mariadb -p<root_password> -e "GRANT ALL PRIVILEGES ON *.* TO '<db_user>'@'%';"` to provision the user's access to the test DB
   1. `<root_password>` being the value of the `TEST_DB_ROOT_PASSWORD` in the .env file
   2. `<db_user>` being the value of the `TEST_DB_USER` in the .env file
7. Head to `http://127.0.0.1:8000/sitepanel` to ensure the project is running locally
8. The Docker containers can be stopped in one of two ways:
   1. Run `docker stop $(docker ps -a -q)` in the terminal
   2. Manually stopping the `wedding-website-backend` container the Docker Desktop Dashboard

## Subsequent Installation

After the first installation, you will no longer need to provision the user's database access. Complete the below steps to run the project locally for any subsequent installations:

1. Run `docker-compose -f ./docker-compose-local.yaml up -d` from the terminal
   1. The container will run in the background
2. Head to `http://127.0.0.1:8000/sitepanel` to ensure the project is running locally
3. The Docker containers can be stopped in one of two ways:
   1. Run `docker stop $(docker ps -a -q)` in the terminal
   2. Via the Docker Dashboard

## Tracking Container Logs

You can track the `web-1` container's logs while it is running. To do so:

- Run `docker-compose logs -f web` from the terminal

## Testing

You will not be able to run unit tests from without first completing step 5 in the [**_First Installation_**](#First-Installation) section first.

Run the following commands from the terminal:

- All unit tests - `docker exec wedding-website-backend-web-1 ./manage.py test --settings=WeddingWebsiteBackend.test_settings`
- Unit tests for a single app - `docker exec wedding-website-backend-web-1 ./manage.py test <app_name> --settings=WeddingWebsiteBackend.test_settings`


## DB Migrations

Run the following commands from the terminal:

- Make migrations files - `docker exec wedding-website-backend-web-1 ./manage.py makemigrations`
- Run migrations - `docker exec wedding-website-backend-web-1 ./manage.py migrate`

## Installing Packages

Run the following commands from the terminal:

- Install package - `docker exec wedding-website-backend-web-1 pip install <package_name>`
- Add to requirements.txt - `docker exec wedding-website-backend-web-1 pip freeze > requirements.txt`

## Collect Static Files

Run the following commands from the terminal:

- Collect static files - `docker exec wedding-website-backend-web-1 ./manage.py collectstatic`
