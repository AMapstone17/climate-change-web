# Climate Champs

## 🧑🏻‍🏭 Installation

Climate Champs is written with Python and Flask. We recommend using Python 3.11 or higher.

First, clone the repository. And optionally, switch to the `release` branch. The `dev` branch was set as the default for
ease of development. However, both branches are up-to-date with each other as of the submission date.

```bash
git clone https://github.com/newcastleuniversity-computing/CSC2033_Team33_23-24.git
git checkout release
```

## ▶️ Running the project

Docker is the preferred way to run the project. After installing Docker, use Docker Compose to run the project.

```bash
docker compose up
```

This will build the image and run both the Flask app and the PostgreSQL database. The app will be available at
`http://localhost:5000`.

The submission files includes a prefilled `.env.docker.local` file, so no configuration will be required. See the
[structure section](#-structure) for more information on the project layout.

## 🧪 Testing

Tests are written using Pytest, and are automated using a GitHub Actions workflow on push and pull requests. To run the
tests locally, run `pytest` from the terminal. A testing and coverage report will be created in the `reports/`
directory.

Testing documentation, including an overview of the testing strategy, can be found in the `TESTING.md` file.

## 🧱 Structure

The project is structured as follows:

```plaintext
CSC2033_Team33_23-24/
├── flaskapp/
│   ├── admin/, groups/, home/, quiz/, users/ # views and forms
│   ├── static, templates # html, css, js
│   ├── models/
│   │   └── user.py, quiz.py, etc.
│   ├── __init__.py # main Flask configuration, create_app, etc.
│   ├── extensions.py # database, extra decorators, setup
│   └── reset.py # database reset
├── test/
│   └── unit/
│       ├── test_config.py
│       └── test_...
├── .env.example, .env.docker.example # example .env files for reference
├── .env.local, .env.docker.local # actual .env files
├── docker-compose.yml # docker compose config for container orchestration
├── Dockerfile # used to build the Flask web app container
├── requirements.txt # all app requirements
└── run.py # main entrypoint
```

