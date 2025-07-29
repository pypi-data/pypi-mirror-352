from plone.restapi.deserializer import json_body
from Products.Five.browser import BrowserView

import json


class rssfeedView(BrowserView):
    # def __init__(self, context, request):
    #     self.context = context
    #     self.request = request

    def __call__(self):
        query = json_body(self.request)

        return json.dumps(query)
