
def rgbansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def gradient(text, start_color, end_color):
    total_length = len(text)

    for i, char in enumerate(text):
        ratio = min(1, (i / total_length) * 1.5)

        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

        print(f"{rgbansi(r, g, b)}{char}", end="")

    print("\033[0m")
