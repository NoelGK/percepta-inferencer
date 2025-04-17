FROM pytorch/pytorch:latest

# General dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Python dependencies
WORKDIR /tmp
  
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN pip install --upgrade pip wheel poetry setuptools
RUN poetry config virtualenvs.create false --local
ENV PEP517_BUILD_BACKEND="setuptools.build_meta"
RUN poetry install --only main --no-root
