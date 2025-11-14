from src.config import get_settings

def main() -> None:
    settings = get_settings()
    print(settings.environment, settings.storage_level)

if __name__ == "__main__":
    main()
