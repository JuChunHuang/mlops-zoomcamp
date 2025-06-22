# 04-deployment-homework

This project demonstrates how to build and run a Docker container for a Python application using `pipenv` for dependency management.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your Mac.
- Apple Silicon (M1/M2) users: Use the `--platform=linux/amd64` flag for compatibility.

## Building the Docker Image

Open your terminal in this directory and run:

```bash
docker build --platform=linux/amd64 -t 04-deployment-homework:v1 .
```

## Running the Docker Container

After building the image, run:

```bash
docker run --platform=linux/amd64 --rm 04-deployment-homework:v1
```

This will execute the starter.py script inside the container using the arguments specified in the Dockerfile.

## Notes

- You have already installed dependencies locally with pipenv install scikit-learn==1.5.0 flask and activated your environment with pipenv shell.

- The Docker build process will install all dependencies listed in the Pipfile inside the container, so your local environment does not affect the container.