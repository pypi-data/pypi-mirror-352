import logging
from argparse import ArgumentParser, BooleanOptionalAction
from secrets import SystemRandom
from shutil import which
from subprocess import run
from typing import List

# Enable logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.WARNING,
    filename="vikinglotto.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


def generate_main_numbers(generator: SystemRandom, euro: bool) -> List[int]:
    # Generate main numbers
    result = []

    try:
        max_number = 48 if not euro else 50
        select_numbers = 6 if not euro else 5
        result = generator.sample(list(range(1, max_number + 1)), select_numbers)
        result.sort()
    except Exception as e:
        logger.warning(f"Generate main numbers error: {e}", exc_info=True)

    return result


def generate_bonus_numbers(generator: SystemRandom, euro: bool) -> List[int]:
    # Generate bonus numbers
    result = []

    try:
        result = [generator.randint(1, 5)] if not euro else generator.sample(list(range(1, 12 + 1)), 2)
        result.sort()
    except Exception as e:
        logger.warning(f"Generate bonus numbers error: {e}", exc_info=True)

    return result


def generate_text(main_numbers: List[int], bonus_numbers: List[int]) -> str:
    # Generate predict text string
    result = ""

    try:
        result = f"Main numbers:\t" + " ".join(f"({n:02})" for n in main_numbers) + "\n\n"
        bonus_prefix = "Bonus number:\t" if len(bonus_numbers) == 1 else "Bonus numbers:\t"
        bonus_text = " ".join(f"({n:02})" for n in bonus_numbers)
        result += bonus_prefix + bonus_text
    except Exception as e:
        logger.warning(f"Generate text error: {e}", exc_info=True)

    return result


def print_log(text: str) -> bool:
    # Print numbers to log file
    result = False 

    try:
        text = text.replace("\n\n", "\n")
        logger.warning(f"------------------------\n\n"
                       f"{text}\n")
        result = True
    except Exception as e:
        logger.warning(f"Print log error: {e}", exc_info=True)
    
    return result


def show_cowsay(text: str) -> bool:
    # Print cowsay
    result = False

    try:
        if which("cowsay") is None:
            print("\nPlease install cowsay. Otherwise, please use --plain flag\n")
            return False

        print()
        run(f"cowsay -W 100 '\n\n{text}\n\n\b'", shell=True)
        print()
        print_log(text)
        result = True
    except Exception as e:
        logger.warning(f"Show cowsay error: {e}", exc_info=True)

    return result


def show_plain(text: str) -> bool:
    # Print directly
    result = False

    try:
        text = text.replace("\n\n", "\n")
        print(f"\n{text}\n")
        print_log(text)
        result = True
    except Exception as e:
        logger.warning(f"Show plain error: {e}", exc_info=True)

    return result


def show_text(plain: bool, text: str) -> bool:
    # Print the final result
    result = False

    try:
        result = show_plain(text) if plain else show_cowsay(text)
    except Exception as e:
        logger.warning(f"Show text error: {e}", exc_info=True)

    return result


def main() -> bool:
    # Main function
    result = False

    try:
        parser = ArgumentParser()
        parser.add_argument("--plain", action=BooleanOptionalAction, help="print the result in plain mode")
        parser.add_argument("--euro", action=BooleanOptionalAction, help="generate numbers for Eurojackpot")
        args = parser.parse_args()

        secret_generator = SystemRandom()
        main_numbers = generate_main_numbers(secret_generator, args.euro)
        bonus_numbers = generate_bonus_numbers(secret_generator, args.euro)
        text = generate_text(main_numbers, bonus_numbers)
        show_text(args.plain, text)
        result = True
    except Exception as e:
        logger.warning(f"Main error: {e}", exc_info=True)

    return result


if __name__ == "__main__":
    main()
