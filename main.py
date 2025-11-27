import argparse
from src.config import load_config
from strategies.generic_chop_and_bank import GenericChopAndBank

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/draynor_willows.json")
    args = parser.parse_args()
    cfg = load_config(args.config)
    GenericChopAndBank(cfg).run()

if __name__ == "__main__":
    main()
