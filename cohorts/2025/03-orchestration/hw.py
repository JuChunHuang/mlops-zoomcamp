#!/usr/bin/env python
# coding: utf-8

import pickle
from pathlib import Path

import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression
from scipy.sparse import hstack

import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)



def read_dataframe(year, month):
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet'

    df = pd.read_parquet(url)
    print(f"Read {len(df)} rows from {url}")

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    return df


def create_X(df, dv=None):
    if dv is None:
        dv_pu = DictVectorizer(sparse=True)
        dv_do = DictVectorizer(sparse=True)
        X_pu = dv_pu.fit_transform(df[["PULocationID"]].to_dict(orient='records'))
        X_do = dv_do.fit_transform(df[["DOLocationID"]].to_dict(orient='records'))
        dv = (dv_pu, dv_do)
    else:
        dv_pu, dv_do = dv
        X_pu = dv_pu.transform(df[["PULocationID"]].to_dict(orient='records'))
        X_do = dv_do.transform(df[["DOLocationID"]].to_dict(orient='records'))
    X = hstack([X_pu, X_do])

    return X, dv


def train_model(X_train, y_train, dv):
    with mlflow.start_run() as run:

        model = LinearRegression()
        model.fit(X_train, y_train)

        print("Model intercept_:", model.intercept_)


        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.sklearn.log_model(model, artifact_path="lr_model_mlflow")

        return run.info.run_id


def run(year, month):
    df_train = read_dataframe(year=year, month=month)
    print(f"Training data: {len(df_train)} rows")

    X_train, dv = create_X(df_train)

    target = 'duration'
    y_train = df_train[target].values

    run_id = train_model(X_train, y_train, dv)
    print(f"MLflow run_id: {run_id}")
    return run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration.')
    parser.add_argument('--year', type=int, required=True, help='Year of the data to train on')
    parser.add_argument('--month', type=int, required=True, help='Month of the data to train on')
    args = parser.parse_args()

    run_id = run(year=args.year, month=args.month)

    with open("run_id.txt", "w") as f:
        f.write(run_id)