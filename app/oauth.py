import json
from rauth import OAuth2Service
from flask import current_app, redirect


class OAuthSignIn:
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTHS'][provider_name]
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.authorize_url = credentials['authorize_url']
        self.token_url = credentials['token_url']
        self.request_url = credentials['request_url']

    def authorize(self):
        pass

    def callback(self, code):
        pass

    def get_callback_url(self):
        return current_app.config['URL'] + '/callback/' + self.provider_name

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class VkSignIn(OAuthSignIn):
    def __init__(self):
        super(VkSignIn, self).__init__('vk')
        self.service = OAuth2Service(
            name='vk',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.token_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='2',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self, code):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if code is None:
            return None

        oauth_session = self.service.get_auth_session(
            data={'code': code,
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )

        user_information = oauth_session.get(
            self.request_url + 'users.get',
            params={'access_token': oauth_session.access_token, 'v': '5.103'}
        ).json()['response'][0]

        friends = oauth_session.get(
            self.request_url + 'friends.get',
            params={'access_token': oauth_session.access_token, 'v': '5.103',
                    'user_id': user_information['id'], 'order': 'random',
                    'count': 5, 'fields': 'bdate'}
        ).json()['response']['items']

        return user_information, friends
