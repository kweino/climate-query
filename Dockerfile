FROM python:3.10-slim

COPY pyproject.toml pyproject.toml

EXPOSE 8501

WORKDIR /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
RUN mkdir -p noaa-storm-data

COPY streamlit_app.py streamlit_app.py
COPY noaa-storm-data/ noaa-storm-data/
COPY scripts/ scripts/

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
