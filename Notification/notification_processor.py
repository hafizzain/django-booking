from firebase_admin.messaging import Message, Notification

from Notification.models import CustomFCMDevice

from Authentication.models import User, AccountType

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



        # only send notification if requerst.user is admin
        if not user.account_type() == 'Employee':
            # may be employee didnt registered a mobile device
            device_registered = CustomFCMDevice.objects.filter(user=user).first()
            if device_registered:
                message = Message(
                    notification=Notification(title=f"{title} Employee ", body=body)
                )
                device_registered.send_message(message)
            else:
                pass
        else:
            device_registered = CustomFCMDevice.objects.filter(user=user).first()
            if device_registered:
                message = Message(
                    notification=Notification(title=f"{title} Admin ", body=body)
                )
                device_registered.send_message(message)
            else:
                pass


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
        else: # single user
            NotificationProcessor.send_notification_per_user(
                user,
                title,
                body
            )


