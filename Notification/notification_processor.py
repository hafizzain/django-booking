from firebase_admin.messaging import Message, Notification

from Notification.models import CustomFCMDevice
from Utility.models import ExceptionRecord

class NotificationProcessor:

    """
    A processor to process push notifications for various events for the employee
    from the admin.
    """

    @staticmethod
    def send_notification_per_user(user, title, body):
        """
        args:
         - user: Employee User
         - title: Commission, Booking etc
         - body: a detailed message
        """

        # may be employee didnt registered a mobile device
        device_registered = CustomFCMDevice.objects.filter(user=user).first()
        # if device_registered:
            # try:
        message = Message(
            notification=Notification(title=title, body=body)
        )

        # get device and send message
        # device = CustomFCMDevice.objects.get(user=user)
        device_registered.send_message(message)
                # except:
                #     ExceptionRecord.objects.create(text='Exception in sendding notification')
        # else:
        #     pass


    @staticmethod
    def send_notifications_to_users(user, title, body):
        """
        A method to handle one or multiple users
        """

        # multiple users
        if type(user) == list:
            user_list = user
            for user in user_list:
                NotificationProcessor.send_notification_per_user(
                    user,
                    title,
                    body
                )
            return "Sent To List"
        else: # single user
            NotificationProcessor.send_notification_per_user(
                user,
                title,
                body
            )
            return "Sent To User"