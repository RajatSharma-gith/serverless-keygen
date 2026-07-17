# Serverless Key Generation Application

An asynchronous, event-driven serverless application built on AWS to securely generate cryptographic keys.

## Architecture

This application is built using modern serverless components to ensure scalability and reliability:

- **Amazon API Gateway**: Serves as the entry point for the REST API.
- **AWS Lambda**: Provides the compute layer for API handlers and background processing.
- **Amazon SQS (Simple Queue Service)**: Decouples the request ingestion from the heavy key generation process.
- **Amazon DynamoDB**: Stores the generated key pairs temporarily, utilizing TTL (Time-To-Live) for automatic cleanup.
- **Amazon ECR (Elastic Container Registry)**: Hosts the custom Docker image required for the processor Lambda.
- **Terraform**: Automates the provisioning of all AWS infrastructure.

### Request Flow
1. **Submit Request**: A user submits a POST request specifying the desired key type and parameters. The API Gateway routes this to the `submit` Lambda function.
2. **Queueing**: The `submit` function validates the inputs, generates a unique `request_id`, places a message on the SQS queue, and returns a `202 Accepted` status with the `request_id`.
3. **Processing**: The SQS queue triggers the Docker-based `processor` Lambda function. This function performs the actual key generation and stores the result securely in DynamoDB.
4. **Fetch Result**: The user can poll the fetch endpoint using their `request_id`. The `fetch` Lambda function queries DynamoDB and returns the generated keys once available.

## Supported Key Types
The API supports generating the following cryptographic key pairs:
*   **RSA**: (2048 or 4096 bits)
*   **ECDSA**: (P-256 or P-384 curves)
*   **Ed25519**

*(Custom expiration times using ISO 8601 UTC format are also supported for automatic deletion)*

## Project Structure

```text
.
├── lambda/
│   ├── submit/      # Python handler for POST /keygen
│   ├── processor/   # Dockerized Python handler for background keygen
│   └── fetch/       # Python handler for GET /keygen/{id}
├── terraform/       # Infrastructure as Code
│   ├── api/         # API Gateway resources
│   ├── infrastructure/ # SQS, DynamoDB, ECR resources
│   ├── lambda/      # Lambda function configurations
│   └── webapp/      # Frontend hosting resources (e.g. S3/CloudFront)
├── webapp/          # Frontend HTML/JS/CSS assets
└── scripts/         # Helper scripts for building and deployment
```

## Deployment Instructions

### Prerequisites
*   [AWS CLI](https://aws.amazon.com/cli/) installed and configured with appropriate credentials.
*   [Terraform](https://www.terraform.io/downloads) (>= 1.0) installed.
*   [Docker](https://www.docker.com/) installed (for building the processor Lambda image).

### Steps
1. Navigate to the terraform directory:
   ```bash
   cd terraform
   ```
2. Initialize the Terraform workspace:
   ```bash
   terraform init
   ```
3. Plan the infrastructure changes:
   ```bash
   terraform plan
   ```
4. Apply the configuration to provision the AWS resources:
   ```bash
   terraform apply
   ```

*Note: Depending on your exact deployment scripts, you may need to build and push the Docker image for the `processor` Lambda to the ECR repository before the Lambda module can be fully applied.*
