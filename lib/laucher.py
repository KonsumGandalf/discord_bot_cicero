from lib.bot import bot
import os

VERSION = "0.0.1"


def main():
    bot.run(VERSION)


if __name__ == '__main__':
    print(f'{os.getcwd()=}')
    main()