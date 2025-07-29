import threading
import time

from printbuddies import print_in_place

from noiftimer import Timer

QUIT = False


class Stopwatch:
    def __init__(self):
        self.quit = False
        self.pause = False
        self.timer = Timer(subsecond_resolution=False)

    @property
    def current_time(self) -> str:
        return f" {self.timer.elapsed_str} "

    def process_input(self):
        value = input()
        if value == "q":
            self.quit = True
        elif value == "r":
            self.timer.reset()
        elif self.timer.is_paused:
            self.timer.unpause()
        else:
            self.timer.pause()

    def intro(self):
        lines = [
            "",
            "Press enter to pause and unpause the timer.",
            "Enter 'r' to restart the timer.",
            "Enter 'q' to quit.",
        ]
        print(*lines, sep="\n")

    def run(self):
        input_thread = threading.Thread(target=self.process_input, daemon=True)
        self.timer.start()
        input_thread.start()
        while input_thread.is_alive() and not self.quit:
            if not self.timer.is_paused:
                print_in_place(self.current_time)
            time.sleep(1)


def main():
    stopwatch = Stopwatch()
    stopwatch.intro()
    while not stopwatch.quit:
        stopwatch.run()


if __name__ == "__main__":
    main()
