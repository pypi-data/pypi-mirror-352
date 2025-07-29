from .WelcomePage import run
import argparse
import os
def main():
    parser = argparse.ArgumentParser(description="CustomTkinterBuilder Software")
    parser.add_argument(
        "command",
        nargs="?",           # Optional positional argument
        default=None,
        help="Create a temp directory"
    )
    args = parser.parse_args()

    if args.command == "temp":
        print("Creating temp directory!")
        try:
            os.mkdir("temp")
        except FileExistsError:
            print("temp directory exists!!")

    print("Running CustomTkinterBuilder")
    run()


if __name__ == "__main__":
    main()