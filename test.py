import json
def read_settings() -> None:
    with open("settings.json") as f:
        settings_info = json.loads(f.read())
    print(settings_info['targetgoods'])


if __name__ == "__main__":
    read_settings()