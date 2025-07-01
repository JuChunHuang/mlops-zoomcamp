from datetime import datetime
import pandas as pd
import os

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_integration():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ['INPUT_FILE_PATTERN'] = 's3://nyc-duration/in/2023-01.parquet'
    os.environ['OUTPUT_FILE_PATTERN'] = 's3://nyc-duration/out/2023-01.parquet'
    os.environ["S3_ENDPOINT_URL"] = "http://localhost:4566"

    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(data, columns=columns)

    options = {
        "client_kwargs": {
            "endpoint_url": os.getenv('S3_ENDPOINT_URL')
        },
        "key": os.getenv('AWS_ACCESS_KEY_ID'),
        "secret": os.getenv('AWS_SECRET_ACCESS_KEY')
    }

    df_input.to_parquet(
        os.getenv('INPUT_FILE_PATTERN'),
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )

    os.system("python ../batch.py 2023 1")

    test_output = pd.read_parquet(os.getenv('OUTPUT_FILE_PATTERN'), storage_options=options)

    assert isinstance(test_output, pd.DataFrame)
    assert len(test_output) == 2
    assert "predicted_duration" in test_output.columns
