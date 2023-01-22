import time
from pprint import pprint
import boto3

JOB_ID = "5e3147084930cc653ec657b7a653e619566e2ef3d76cc7bf4ea8382a8c0f4c5d"


def main():
    textract = boto3.client("textract")

    next_token = None
    while True:
        # You cannot pass NextToken = "" or NextToken = None to the API since it will throw errors:
        # "Invalid type for parameter NextToken, value: None, type: <class 'NoneType'>, valid types: <class 'str'>"
        # "Invalid length for parameter NextToken, value: 0, valid min length: 1"
        if next_token is None:
            response = textract.get_document_text_detection(JobId=JOB_ID)
        else:
            response = textract.get_document_text_detection(
                JobId=JOB_ID, NextToken=next_token)
        if response["JobStatus"] == "SUCCEEDED":
            # Extract text from the response
            for block in response["Blocks"]:
                if block["BlockType"] == "LINE":
                    print(block["Text"])

            # Check if there are more pages to process
            if "NextToken" in response:
                next_token = response["NextToken"]
            else:
                break
        elif response["JobStatus"] == "FAILED":
            raise Exception(f"Job {JOB_ID} failed.")
        else:
            print("Waiting for job to complete...")
            time.sleep(5)

    print("DONE.")


if __name__ == "__main__":
    main()
