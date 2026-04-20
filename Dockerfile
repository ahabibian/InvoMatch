FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=src
ENV INVOMATCH_ENV=production

COPY pyproject.toml /app/pyproject.toml

RUN python -m pip install --upgrade pip
RUN pip install .

COPY . /app

RUN mkdir -p /app/output /app/output/production /app/output/production/artifacts /app/output/production/exports /app/output/production/uploads /app/output/production/tmp /app/output/production/logs

EXPOSE 8000

CMD ["uvicorn", "invomatch.main:app", "--host", "0.0.0.0", "--port", "8000"]