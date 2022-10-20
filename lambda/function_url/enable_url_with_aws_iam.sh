#!/bin/bash
aws lambda create-function-url-config --function-name my_public_hello_world --auth-type NONE

aws lambda add-permission --function-name my_public_hello_world --action lambda:InvokeFunctionUrl --statement-id https --principal "*" --function-url-auth-type NONE --output text
 
