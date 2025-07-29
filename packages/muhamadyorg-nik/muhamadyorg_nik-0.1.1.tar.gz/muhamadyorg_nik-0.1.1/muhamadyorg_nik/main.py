# muhamadyorg_nik/main.py
import pyfiglet
import argparse

def main():
    parser = argparse.ArgumentParser(description="Figlet-style ASCII banner generator")
    parser.add_argument("text", nargs="*", help="Text to convert into ASCII art")
    args = parser.parse_args()

    if args.text:
        text = " ".join(args.text)
    else:
        text = input("nik : ")

    print(pyfiglet.figlet_format(text))
