from firebase_admin.messaging import Message, Notification

from Notification.models import CustomFCMDevice
from Utility.models import ExceptionRecord

class NotificationProcessor:

    """
    A processor to process push notifications for various events for the employee
    from the admin.
    """

    @classmethod
    def send_notification(user, title, body):
        """
        args:
         - user: Employee User
         - title: Commission, Booking etc
         - body: a detailed message
        """

        # prepare message
        try:
            message = Message(
                notification=Notification(title=title, body=body)
            )

            # get device and send message
            device = CustomFCMDevice.objects.get(user=user)
            device.send_message(message)
        except:
            ExceptionRecord.objects.create(text='Exception in sendding notification')