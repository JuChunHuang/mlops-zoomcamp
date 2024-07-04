## Deploying a model as a web-service

* Creating a virtual environment with Pipenv
* Creating a script for predictiong 
* Putting the script into a Flask app
* Packaging the app to Docker


Use the Dockerfile to build the image:

```bash
docker build -t ride-duration-prediction-service:v1 .
```

-it run in interactive mode, --rm remove image after:

```bash
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1
```
