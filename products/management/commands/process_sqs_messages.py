import boto3
import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class SQSService:
    def __init__(self):
        try:
            self.sqs = boto3.client(
                'sqs', 
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.queue_url = self.get_queue_url()
        except Exception as e:
            raise ImproperlyConfigured(f"SQS Configuration Error: {str(e)}")

    def get_queue_url(self):
        """
        Retrieve the SQS Queue URL based on queue name in settings
        """
        try:
            response = self.sqs.get_queue_url(QueueName=settings.SQS_QUEUE_NAME)
            return response['QueueUrl']
        except Exception as e:
            raise ImproperlyConfigured(f"Could not retrieve SQS Queue URL: {str(e)}")

    def send_order_message(self, order):
        """
        Send order details to SQS queue
        """
        try:
            message_body = json.dumps({
                'order_id': order.id,
                'user_id': order.user.id,
                'total_cost': float(order.total_cost),
                'address': order.address,
                'phone': order.phone,
                'status': order.status
            })

            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body
            )
            return response['MessageId']
        except Exception as e:
            print(f"Error sending message to SQS: {str(e)}")
            return None

    def receive_messages(self, max_messages=10):
        """
        Receive messages from the SQS queue
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20  # Long polling
            )
            
            return response.get('Messages', [])
        except Exception as e:
            print(f"Error receiving messages from SQS: {str(e)}")
            return []

    def delete_message(self, receipt_handle):
        """
        Delete a message from the queue after processing
        """
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        except Exception as e:
            print(f"Error deleting message from SQS: {str(e)}")

def process_sqs_messages():
    """
    Utility function to process SQS messages
    Can be called via management command or background task
    """
    sqs_service = SQSService()
    messages = sqs_service.receive_messages()

    for message in messages:
        try:
            body = json.loads(message['Body'])
            order_id = body.get('order_id')
            
            # Additional processing logic here
            # For example, update order status, send notifications, etc.
            
            # Delete message after processing
            sqs_service.delete_message(message['ReceiptHandle'])
        except Exception as e:
            print(f"Error processing SQS message: {str(e)}")

# Example usage in thank_you view
def thank_you(request):
    # ... existing order creation logic ...
    
    # After successfully creating order
    sqs_service = SQSService()
    sqs_service.send_order_message(order)
    
    return render(request, 'thank_you.html', {'order_id': order.id})