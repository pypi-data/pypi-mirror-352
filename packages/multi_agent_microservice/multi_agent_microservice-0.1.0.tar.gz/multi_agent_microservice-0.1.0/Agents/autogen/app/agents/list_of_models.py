import boto3

# Create a Bedrock client
client = boto3.client('bedrock', region_name='us-west-2')

# Call the list_foundation_models API
response = client.list_foundation_models()

print(response)
