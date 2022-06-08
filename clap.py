from piclap import *
import requests

class XListener(Listener):
    def listenClaps(self, threadName):
        with self.lock:
            print("Waiting for claps...")
            self.clapWait(self.claps)
            self.config.onClaps(self.claps)
            print("You clapped", self.claps, "times.\n")
            self.claps = 0


class Config(Settings):
    def __init__(self):
        Settings.__init__(self)
        self.method.value = 1536
        self.active = False

    def onClaps(self, claps):
        if claps < 2:
            return

        if self.active:
            setEffect({
                'effect': 'set',
                'r': 0,
                'g': 0,
                'b': 0,
            })
            self.active = False
        else:
            setEffect({
                'effect': 'wipe',
                'r': 0,
                'g': 117,
                'b': 225,
            })
            self.active = True


def setEffect(data):
    requests.post('http://localhost:50390/api/effect', json=data)


if __name__ == '__main__':
    config = Config()
    listener = XListener(config=config, calibrate=False)
    listener.start()
