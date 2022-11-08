FROM python:3.10

COPY pyproject.toml pyproject.toml

WORKDIR /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
RUN mkdir -p noaa-storm-data

COPY noaa-storm-data/NOAA_filenames.csv noaa-storm-data/NOAA_filenames.csv
COPY scripts/ scripts/

ENTRYPOINT [ "python", "scripts/noaa_ingest_to_parquet.py"]
