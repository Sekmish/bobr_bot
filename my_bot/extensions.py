import requests


class APIException(Exception):
    pass

class BusSchedule:
    YANDEX_API_URL = "https://api.rasp.yandex.net/v3.0/search/"

    @staticmethod
    def get_bus(start_bus, end_bus, date_bus, yandex_api_key):
        payload = {
            "from": start_bus,
            "to": end_bus,
            "format": "json",
            "apikey": yandex_api_key,
            "date": date_bus,
            "transport_types": "bus"
        }

        response = requests.get(BusSchedule.YANDEX_API_URL, params=payload)
        data = response.json()

        if response.status_code != 200:
            raise APIException("Ошибка при получении данных от API")

        return data["segments"]


