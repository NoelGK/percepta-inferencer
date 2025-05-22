FROM pytorch/pytorch:latest

# General dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Python dependencies
WORKDIR /tmp
  
COPY ./pyproject.toml ./poetry.lock* /tmp/

ENV PEP517_BUILD_BACKEND="setuptools.build_meta"
RUN pip install --upgrade pip wheel poetry setuptools && \
    poetry config virtualenvs.create false --local && \
    poetry install --only main --no-root

WORKDIR /app
COPY ./ /app/
ENV PYTHONPATH="/app/src"
ENV PYTHONDONTWRITEBYTECODE=1
CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:api", "--bind", "0.0.0.0:8000" ]
