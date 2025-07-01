#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import pandas as pd


def read_data(filename):
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')

    if s3_endpoint_url:
        options = {
        "client_kwargs": {
            "endpoint_url": "http://localhost:4566"
        },
        "key": os.getenv('AWS_ACCESS_KEY_ID'),
        "secret": os.getenv('AWS_SECRET_ACCESS_KEY')
        }
        return pd.read_parquet(filename, storage_options=options)
    
    return pd.read_parquet(filename)


def save_data(df_result, output_file):
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')

    if s3_endpoint_url:
        options = {
        "client_kwargs": {
            "endpoint_url": "http://localhost:4566"
        },
        "key": os.getenv('AWS_ACCESS_KEY_ID'),
        "secret": os.getenv('AWS_SECRET_ACCESS_KEY')
        }
        df_result.to_parquet(output_file, engine='pyarrow', index=False, storage_options=options)
    else:
        df_result.to_parquet(output_file, engine='pyarrow', index=False)


def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def prepare_data(df, columns, year, month):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[columns] = df[columns].fillna(-1).astype('int').astype('str')
    
    return df


def get_model(path):
    with open(path, 'rb') as f_in:
        dv, lr = pickle.load(f_in)
    return dv, lr


def post_process(df, y_pred):
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    return df_result


def main(year, month):
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    categorical = ['PULocationID', 'DOLocationID']
    dv, lr = get_model('../model.bin')
    df = read_data(input_file)
    df = prepare_data(df, categorical, year, month)

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())
    df_result = post_process(df, y_pred)
    save_data(df_result, output_file)


if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    
    main(year, month)