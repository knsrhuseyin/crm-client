from colorama import init, Fore, Style

init(autoreset=True)


class Logger:
    def __init__(self, name):
        self.name = name

    def log(self, text):
        logger_name = Style.BRIGHT + self.name
        print(logger_name + " " + text)

    def error(self, text):
        self.log(Fore.RED + text)

    def warning(self, text):
        self.log(Fore.YELLOW + text)

    def great(self, text):
        self.log(Fore.GREEN + text)