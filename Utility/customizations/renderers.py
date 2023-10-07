from rest_framework.renderers import BaseRenderer
import json

class CustomRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'

    def render(self, data, media_type=None, renderer_context=None):
        # Implement your custom rendering logic here
        # You can return the JSON representation of your data
        response = data.get('response', None)
        if response:
            message = response.get('message', None)
            if message:
                message = message.capitalize()
                data['response']['message'] = message
        return json.dumps(data, ensure_ascii=False).encode('utf-8')