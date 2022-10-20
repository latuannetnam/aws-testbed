import boto3

#Main
print("List all S3 resources")
s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
    print("Bucket:" + bucket.name)
    
