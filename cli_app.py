from pass24_api_client.api_client import Pass24ApiClient, AuthError, ResponseStatusError, RequestError, create_pass

if __name__ == '__main__':
    phone = '79991234567'
    password = 'password'
    plate_number = 'АБВ123'

    res = create_pass(phone, password, plate_number, 'Audi', 'Такси')
    print(res)

