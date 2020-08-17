import aiohttp
import json
import os

from tomon_sdk.network.route import Route

class HackRoute(Route):
    def __init__(self, route: Route):
        self.path = route.path
        self.token = route.token
        self.url = route.url

    async def request(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})
        payload = kwargs.get('payload', {})

        if not ('auth' in kwargs.keys() and kwargs['auth'] == False):
            headers['authorization'] = self.auth()

        if 'files' in kwargs.keys():
            payload = aiohttp.FormData()
            if len(kwargs['files']) == 1:
                filepath = kwargs['files'][0]
                filename = os.path.basename(filepath)
                payload.add_field('file', open(
                    filepath, 'rb'), filename=filename)
            else:
                for index, file in enumerate(list(kwargs['files'])):
                    payload.add_field(
                        'file'+str(index), open(file, 'rb'), filename=os.path.basename(file))

        if 'data' in kwargs.keys():
            payload.add_field('payload_json', json.dumps(kwargs['data']))
        
        try:
            async with aiohttp.request(method=method, url=url, data=payload, headers=headers) as r:
                if 300 > r.status >= 200:
                    return await r.json()
                elif r.status == 404:
                    print("Not Found")
                elif r.status == 403:
                    print("Forbidden")
                else:
                    print(await r.json())

        except Exception as e:
            print(e)
    
    async def post(self, **kwargs):
        return await self.request('POST', self.url, **kwargs)

    async def get(self, **kwargs):
        return await self.request('GET', self.url, **kwargs)

    async def patch(self, **kwargs):
        return await self.request('PATCH', self.url, **kwargs)

    async def put(self, **kwargs):
        return await self.request('PUT', self.url, **kwargs)

    async def delete(self, **kwargs):
        return await self.request('DELETE', self.url, **kwargs)