import boto3
from pprint import pprint

FILENAME = "sample.pdf"
S3_BUCKET = "textract-sample-000000000000"
INPUT_PREFIX = f"input/{FILENAME}"
ROLE_ARN = "arn:aws:iam::000000000000:role/TextractSampleRole"
SNS_TOPIC = "arn:aws:sns:us-east-1:000000000000:AmazonTextractSampleCompletionNotifications"


def main():
    # Upload sample PDF file to S3
    s3 = boto3.client("s3")
    s3.upload_file(FILENAME, S3_BUCKET, INPUT_PREFIX)
    print(f"Uploaded sample.pdf to s3://{S3_BUCKET}/{INPUT_PREFIX}")

    # Use Amazon Textract to detect text in the sample PDF file
    textract = boto3.client("textract")
    response = textract.start_document_text_detection(
        DocumentLocation={"S3Object": {
            "Bucket": S3_BUCKET, "Name": INPUT_PREFIX}},
        OutputConfig={"S3Bucket": S3_BUCKET, "S3Prefix": "output"},
        NotificationChannel={"RoleArn": ROLE_ARN, "SNSTopicArn": SNS_TOPIC},
    )
    pprint(response)
    print("DONE.")


if __name__ == "__main__":
    main()
