FROM python:3.10 as builder
RUN mkdir -p /beauty
WORKDIR /beauty
COPY pyproject.toml poetry.lock /beauty/
ENV POETRY_VIRTUALENVS_CREATE false
RUN pip3 install pip --upgrade && pip3 install poetry --upgrade --pre && poetry install --no-root --only main

FROM python:3.10-slim
WORKDIR /beauty
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY . /beauty
CMD ["uvicorn" ,"beauty.app:app", "--host", "0.0.0.0"]
