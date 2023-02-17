FROM mcr.microsoft.com/playwright/python:v1.30.0-focal
RUN mkdir -p /beauty
WORKDIR /beauty
COPY pyproject.toml poetry.lock /beauty/
ENV POETRY_VIRTUALENVS_CREATE false
RUN pip3 install poetry --upgrade --pre
RUN poetry install --no-root --only main
COPY . /beauty
CMD ["uvicorn" ,"beauty.app:app", "--host", "0.0.0.0"]
