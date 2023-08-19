from firebase_admin.messaging import Message, Notification

from Notification.models import CustomFCMDevice
from Utility.models import ExceptionRecord

class NotificationProcessor:

    """
    A processor to process push notifications for various events for the employee
    from the admin.
    """

    @classmethod
    def send_notification_per_user(user=None, title=None, body=None):
        """
        args:
         - user: Employee User
         - title: Commission, Booking etc
         - body: a detailed message
        """

        # may be employee didnt registered a mobile device
        is_device_registered = CustomFCMDevice.objects.filter(user=user).first()
        if is_device_registered:
            try:
                message = Message(
                    notification=Notification(title=title, body=body)
                )

                # get device and send message
                device = CustomFCMDevice.objects.get(user=user)
                device.send_message(message)
            except:
                ExceptionRecord.objects.create(text='Exception in sendding notification')
        else:
            pass


    @classmethod
    def send_notifications_to_users(users, title, body):
        """
        A method to handle one or multiple users
        """

        # multiple users
        if type(users) == list:
            for user in users:
                NotificationProcessor.send_notification_per_user(
                    user=user,
                    title=title,
                    body=body
                )
        else: # single user
            NotificationProcessor.send_notification_per_user(
                user=users,
                title=title,
                body=body
            )