from server import app, client
import threading

#threading.Thread(target=lambda: app.start()).start()
threading.Thread(target=lambda: client.start()).start()
