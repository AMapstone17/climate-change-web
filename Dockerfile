FROM python:3.12-alpine
LABEL authors="tomc128"

RUN apk update && \
    apk add musl-dev libpq-dev gcc

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV IS_DOCKER=True

COPY climate-change-web .

ENTRYPOINT ["python3", "-m", "flask", "--app", "run", "run", "--host=0.0.0.0"]