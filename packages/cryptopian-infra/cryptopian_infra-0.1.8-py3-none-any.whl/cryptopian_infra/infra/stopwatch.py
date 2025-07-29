import logging
import time


class Stopwatch(object):
    def __init__(self, topic, level=logging.DEBUG):
        self.topic = topic
        self.logging_level = level
        self.logger = logging.getLogger(f"Stopwatch[{topic}]")
        self.start_time = None
        self.duration = None

    def start(self):
        if self.start_time is None:
            self.start_time = time.time()

    def stop(self):
        self.duration = time.time() - self.start_time

    def reset(self):
        self.start_time = None
        self.duration = None

    def restart(self):
        self.reset()
        self.start()

    def __enter__(self):
        self.restart()
        self.__log("started")

    def __log(self, message):
        if self.logger.isEnabledFor(self.logging_level):
            self.logger.log(self.logging_level, message)
        else:
            print(self.topic, message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.__log(f"finished {self.duration} s")
