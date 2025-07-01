# 06-best-practices Homework

This project demonstrates best practices for Python environment management using `pipenv` and `pyenv` on macOS.

## Environment Setup

Follow these steps to set up your environment without affecting your global Python installation.

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, you may need to add Homebrew to your shell profile.

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. Install pyenv

```bash
brew install pyenv
```

### 3. Install Python 3.10 (based on the requirement)

```bash
pyenv install 3.10.14
```

### 4. Set Local Python Version

In your project directory, run

```bash
pyenv local 3.10.14
```

### 5. Install Project Dependencies and Activate the pipenv Shell

```bash
pipenv install
pipenv shell
```

### 6. Clean Up (After Finishing the Project)

To remove the pipenv environment:

```bash
pipenv --rm
```

To remove pyenv and all installed Python version;

```bash
rm -rf ~/.pyenv
```


# S3 Integration Test Environment with Localstack

This guide explains how to set up a local S3 environment for integration testing using [Localstack](https://github.com/localstack/localstack) and the AWS CLI. This allows you to mimic AWS S3 locally without needing a real AWS account.

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed and running
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed

### 1. Start Localstack with Docker Compose

A `docker-compose.yaml` has been created. To start Localstack, run:

```bash
docker-compose up -d
```

### 2. Set AWS CLI Credentials for Localstack

Localstack requires AWS credentials, but any values will work. Set them in your terminal:

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Create an S3 Bucket

Use the AWS CLI to create a bucket named nyc-duration:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration --region us-east-1
```

### 4. Verify the Bucket

```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

### 5. Save a DataFrame to S3

Follow the Python snippet to save a DataFrame to your Localstack S3 bucket:

```python
options = {
    "client_kwargs": {
        "endpoint_url": "http://localhost:4566"
    },
    "key": "test",
    "secret": "test"
}

df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)
```

Verify the file by running:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/
```

If you want to delete the file, run:
```bash
aws --endpoint-url=http://localhost:4566 s3 rm s3://nyc-duration/ --recursive
```

### 6. Clean Up

To stop Localstack and remove data:

```bash
docker-compose down
rm -rf localstack-data
```

### Note:

Always use the `--endpoint-url=http://localhost:4566` flag with AWS CLI commands to interact with Localstack.

These steps allow you to safely test S3 interactions locally without using real AWS resources.