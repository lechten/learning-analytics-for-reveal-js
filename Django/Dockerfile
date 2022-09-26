# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# Pull official base image
FROM python:3.8

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update and install
RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev netcat
RUN pip install --upgrade pip

# Install python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy entrypoint.sh
COPY ./entrypoint.sh .

# Copy project into container
COPY . .

# Run entrypoint.sh for database setup
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]