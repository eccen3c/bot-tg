import requests


class WebhookServiceError(Exception):
    """Класс исключения для ошибок отправки данных на вебхук."""
    pass


def send(data_file, url):
    """Отправляет данные на указанный вебхук."""
    try:
        response = requests.post(url, json=data_file)
        if response.status_code != 200:
            raise WebhookServiceError(f"Failed to send data")
    except requests.RequestException as e:
        raise WebhookServiceError(f"Error during request")
