from src.config import load_config
from src.bot import WillowBot

def main() -> None:
    cfg = load_config()
    bot = WillowBot(cfg)
    bot.run()

if __name__ == "__main__":
    main()

