FROM python:3.11.8-slim-bookworm as requirements-stage

WORKDIR /tmp

RUN pip install --no-cache-dir poetry==1.8.2

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export \
    --format requirements.txt \
    --output requirements.txt \
    --without-hashes

FROM python:3.11.8-slim-bookworm

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

CMD ["python", "main.py"]
