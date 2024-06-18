import webbrowser

def start(port):
    webbrowser.open(f"http://127.0.0.1:{port}", 1, True)

if __name__ == "__main__":
    start()
