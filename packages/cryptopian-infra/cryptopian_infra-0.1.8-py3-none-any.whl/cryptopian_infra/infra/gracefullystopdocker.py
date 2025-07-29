import signal


def handle_sigterm(signals, frame_type):
    raise KeyboardInterrupt()


def gracefully_stop_docker():
    signal.signal(signal.SIGTERM, handle_sigterm)
