import requests


def handle_updates(data):
    status = data.get("status")

    if status == "found":
        new_attempts = data.get("new_attempts", [])
        last_attempt_timestamp = data.get("last_attempt_timestamp")

        # Обработка новых попыток или других данных по мере необходимости.
        print(f"New attempts: {new_attempts}")
        print(f"Last attempt timestamp: {last_attempt_timestamp}")

    elif status == "timeout":
        timestamp_to_request = data.get("timestamp_to_request")
        # Обработка ситуации, когда больше нет свежих работ.
        print(f"Timeout. Timestamp to request: {timestamp_to_request}")

    # Другие возможные статусы могут быть добавлены в логику обработки.


def long_polling_example():
    url = "https://dvmn.org/api/long_polling/"
    params = {}  # Здесь могут быть необходимые параметры запроса, например, токен доступа и другие.

    while True:
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()
            handle_updates(data)

        except requests.exceptions.RequestException as e:
            print(f"Error during long polling: {e}")


if __name__ == "__main__":
    long_polling_example()
