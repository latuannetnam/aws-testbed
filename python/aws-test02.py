import boto3

print("Test SQS")
sqs = boto3.resource('sqs')

# Print all queues
for queue in sqs.queues.all():
    print("Queue name:", queue.url)

# Create queue
queue = sqs.create_queue(QueueName='TestQueue')
print("created Queue name:" + queue.url)
print("Queue attribute:{}".format(queue.attributes))

#  Get queue by name
queue = sqs.get_queue_by_name(QueueName='TestQueue')
print("Get queue:" + queue.url)