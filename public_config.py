import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    URL = 'https://96e62f61c7eb.ngrok.io'
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OAUTHS = {
        'vk': {
            'client_id': 12345,
            'client_secret': '',
            'authorize_url': 'https://oauth.vk.com/authorize',
            'token_url': 'https://oauth.vk.com/access_token',
            'request_url': 'https://api.vk.com/method/'
        }
    }
