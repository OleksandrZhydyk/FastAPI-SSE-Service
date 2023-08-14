FROM python:3.10

RUN apt update

RUN mkdir "notification_service"

WORKDIR /notification_service

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./poetry.lock ./
COPY ./pyproject.toml ./

RUN python -m pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY ./src ./src

EXPOSE 8001

CMD [ "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
