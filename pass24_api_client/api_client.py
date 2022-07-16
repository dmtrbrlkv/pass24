import datetime
from enum import Enum
from http import HTTPStatus

import pytz as pytz
import requests as requests


class RequestMethod(Enum):
    GET = 'get'
    POST = 'post'


class AuthError(BaseException):
    pass


class ResponseStatusError(BaseException):
    pass


class RequestError(BaseException):
    pass


class Pass24ApiClient:
    BASE_URL = 'https://mobile-api.pass24online.ru/v1/'

    def __init__(self, phone, password):
        self.phone = phone
        self.password = password
        self.token = None
        self.vehicle_models = None
        self.options = None

    def get(self, path, body=None, need_token=True, ok_status=HTTPStatus.OK, as_json=True):
        return self.request(RequestMethod.GET, path, body, need_token, ok_status, as_json)

    def post(self, path, body=None, need_token=True, ok_status=HTTPStatus.OK, as_json=True):
        return self.request(RequestMethod.POST, path, body, need_token, ok_status, as_json)

    def request(self, method, path, body, need_token, ok_status, as_json):
        url = self.BASE_URL + path
        if need_token:
            if body is None:
                body = {}
            body.update({'token': self.get_token()})
        if method == RequestMethod.GET:
            response = requests.get(url, json=body)
        elif method == RequestMethod.POST:
            response = requests.post(url, json=body)
        else:
            raise ValueError(f'Unknown method: {method}')
        if ok_status and response.status_code != ok_status:
            raise ResponseStatusError(
                f'Wrong response status code: {response.status_code}, response text: {response.text}')
        if as_json:
            return response.json()
        return response

    def get_token(self):
        path = 'auth/login'
        if not self.token:
            body = {
                'phone': self.phone,
                'password': self.password
            }
            json_data = self.post(path, body, need_token=False)
            if json_data['error']:
                raise AuthError(json_data['error'])
            self.token = json_data['body']
        return self.token

    def get_vehicle_models(self):
        path = 'vehicle-models'
        if not self.vehicle_models:
            json_data = self.get(path, body=None, need_token=False)
            if json_data['error']:
                raise RequestError(json_data['error'])
            response_vehicle_models = json_data['body']
            vehicle_models = {}
            for vehicle_model in response_vehicle_models:
                vehicle_models[vehicle_model['name']] = vehicle_model['id']
            self.vehicle_models = vehicle_models
        return self.vehicle_models

    def get_vehicle_models_names(self):
        vehicle_models = self.get_vehicle_models()
        return list(vehicle_models.keys())

    def get_object_options(self):
        path = 'profile/objects'
        if not self.options:
            json_data = self.get(path, body=None)
            if json_data['error']:
                raise RequestError(json_data['error'])
            response_options = json_data['body'][0]['options']
            options = {}
            for option in response_options:
                options[option['name']] = option['id']
            self.options = options
        return self.options

    def get_object_options_name(self):
        options = self.get_object_options()
        return [option['name'] for option in options]

    def get_option_id(self, option):
        options = self.get_object_options()
        if option not in options:
            return None
        return options[option]

    def get_vehicle_model_id(self, vehicle_model):
        vehicle_models = self.get_vehicle_models()
        if vehicle_model not in vehicle_models:
            return None
        return vehicle_models[vehicle_model]

    def get_default_vehicle_model_id(self):
        return self.get_vehicle_model_id('Не задана')

    def get_address_id(self):
        path = 'profile/addresses'
        json_data = self.get(path)
        if json_data['error']:
            raise RequestError(json_data['error'])
        return json_data['body'][0]['id']

    def create_pass(self, plate_number, vehicle_model=None, starts_at=None, option=None, expiration=24):
        path = 'passes'
        address_id = self.get_address_id()
        guest_type = 1
        model_id = None
        if vehicle_model:
            model_id = self.get_vehicle_model_id(vehicle_model)
        if not model_id:
            model_id = self.get_default_vehicle_model_id()

        if not starts_at:
            starts_at = datetime.datetime.now(pytz.timezone('Europe/Moscow')) + datetime.timedelta(minutes=1)
        expires_at = starts_at + datetime.timedelta(hours=expiration)

        if option:
            option_id = self.get_option_id(option)
        else:
            option_id = None

        body = {
            'addressId': address_id,
            'durationType': 1,
            'guestType': guest_type,
            'guestData': {
                'vehicleType': None,
                'modelId': model_id,
                'plateNumber': plate_number
            },
            'startsAt': str(starts_at),
            'expiresAt': str(expires_at),
            "options": [option_id]
        }
        json_data = self.post(path, body)
        if json_data['error']:
            raise RequestError(json_data['error'])
        return json_data['body']


def create_pass(phone, password, plate_number, vehicle_model=None, option=None, expiration=24):
    expiration = int(expiration)
    client = Pass24ApiClient(phone, password)
    try:
        json_data = client.create_pass(plate_number, vehicle_model=vehicle_model, option=option, expiration=expiration)

        plate_number = json_data['guestData']['plateNumber']
        model = json_data['guestData']['model']['name']
        address = json_data['address']['name']
        tenant = json_data['tenant']['name']
        starts_at = json_data['startsAt']
        expires_at = json_data['expiresAt']

        res = f'Создан пропуск для {plate_number} (модель - {model}) к жильцу {tenant} по адресу {address}.' \
              f'Время визита {starts_at} - {expires_at}'

    except AuthError as e:
        res = f'Ошибка авторизации: {e}'

    except (ResponseStatusError, RequestError) as e:
        res = f'Ошибка сервера {e}'

    except BaseException:
        res = 'Неожиданная ошибка'

    return res


def get_vehicle_models():
    return Pass24ApiClient('', '').get_vehicle_models_names()
