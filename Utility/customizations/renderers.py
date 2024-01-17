from rest_framework.renderers import JSONRenderer

class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Implement your custom rendering logic here
        # You can return the JSON representation of your data
        if data:
            response = data.get('response', None)
            if response:
                message = response.get('message', None)
                if message:
                    message = message.capitalize()
                    data['response']['message'] = message
        else:
            pass
        return super().render(data, accepted_media_type, renderer_context)