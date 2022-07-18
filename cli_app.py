import os

from pass24_api_client.api_client import create_pass

if __name__ == '__main__':
    phone = '79991234567'
    password = 'password'
    plate_number = 'АБВ123'
    object_id = os.getenv('OBJECT_ID')

    res = create_pass(phone, password, plate_number, 'Audi', 'Такси', object_id=object_id)
    print(res)

