def log(subsystem: str, msg: str) -> None:
    print(f"[{subsystem}] {msg}")

def print_banner(text: str) -> None:
    print("")
    print("")
    print("         FRC TEAM 1811 - FRESH         ")
    print("")
    print(f"{text.center(39)}")
    print("")
    print("")