#!/usr/bin/env python

import random

import nccapy


class DLA:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.image = nccapy.Canvas(width, height)
        self.image.clear(255, 255, 255, 255)

    def random_seed(self) -> None:
        x = random.randint(1, self.width - 1)
        y = random.randint(1, self.height - 1)
        self.image.put_pixel(x, y, 0, 0, 0, 0)

    def _random_start(self):
        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        return x, y

    def _clear_walk_path(self):
        # search for red pixels with alpha of 128 and set them back to white
        for x in range(0, self.width):
            for y in range(0, self.height):
                r, g, b, a = self.image.get_pixel(x, y)
                if r == 255 and g == 0 and b == 0:  # and a == 128 :
                    self.image.put_pixel(x, y, 255, 255, 255, 255)

    def walk(self) -> bool:
        x, y = self._random_start()
        walking = True
        found = False

        while walking:
            while True:
                if not (1 <= x <= self.width - 2) or not (1 <= y <= self.height - 2):
                    # print(f"hit edge {x} {y}")
                    walking = False
                    found = False
                    self._clear_walk_path()
                    break

                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                r, g, b, a = self.image.get_pixel(x, y)
                if r == 255 and g == 0 and b == 0:
                    continue
                else:
                    break

            # check we are in bounds
            if not (1 <= x <= self.width - 2) or not (1 <= y <= self.height - 2):
                # print(f"hit edge {x} {y}")
                walking = False
                found = False
                self._clear_walk_path()
                break
            # now check if we are near the seed
            else:
                steps = [-1, 0, 1]
                for x_offset in steps:
                    for y_offset in steps:
                        try:
                            r, g, b, a = self.image.get_pixel(
                                x + x_offset, y + y_offset
                            )
                            self.image.put_pixel(
                                x + x_offset, y + y_offset, 255, 0, 0, 128
                            )
                            if r == 0 and g == 0 and b == 0:
                                self.image.put_pixel(x, y, 0, 0, 0, 255)

                                walking = False
                                found = True
                                self._clear_walk_path()
                                break

                        except IndexError:
                            print("index error not sure why")
                            walking = False
                            found = False
                            break
                self.image.update()
        return found


def run_sim(width: int, height: int, num_seeds: int = 100):
    dla = DLA(width, height)
    # for _ in range(0, num_seeds):
    #     dla.random_seed()
    for _ in range(0, width):
        dla.image.put_pixel(_, height // 2, 0, 0, 0, 0)
    while not dla.image.should_quit():
        dla.walk()
        dla.image.update()


if __name__ == "__main__":
    run_sim(400, 200, 500)
