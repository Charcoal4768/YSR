#product grade multithreading / multiprocess support, local host debugging fallback using if __name__
from mainSite import app, socket

if __name__ == '__main__':
    socket.run(app, host="0.0.0.0", debug=True)
