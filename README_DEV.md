
This README provides information on how to set up the project locally and run the
app. Please refer to the [main README](README.md) for general information about the project.

## Running the Project

### Docker

Duplicate the `.env.docker.example` file and call it `.env.docker.local`. This is used in the Docker configuration.

If using Pycharm, it's recommended to edit the Docker run configuration. Click More Options and then set Build to
always. This prevents you from having to run `docker compose build` every time you make a change.

#### Full Docker (production)

To run the app in Docker, run `docker compose up` from the terminal. This will build the image and run the container.
Alternatively, open `docker-compose.yml` in PyCharm and run the configuration from there (double green arrow at the
top).

#### Partial Docker (development)

It's possible to run Flask locally, but connect to the database in Docker. To do this, run only the database container
(and optionally the adminer container) with `docker compose up db (adminer)`. Edit your `.env.local` file and set the
database URI to `postgresql://postgres:[password]@localhost:5432/postgres`. Where `[password]` should be replaced with
the password in `.env.docker.local`.

### Locally

Duplicate the `.env.example` file and call it `.env.local`. This is the actual file Python will read environment
variables from.

You'll need to manually install the requirements with `pip install -r requirements.txt`.

To run the project, either run `python -m flask --app run run` from the terminal, or set up a Flask configuration in
PyCharm (choosing script and run.py as the path), and run it from there.
