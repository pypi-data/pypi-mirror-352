from typing import Tuple

import PIL.Image

from .RGBA import RGBA


class ImageXBoundsError(Exception):
    """ "x index in set or get pixel is out of bounds"""


class ImageYBoundsError(Exception):
    """ "y index in set or get pixel is out of bounds"""


class Image:
    """
    A class to represent an image.
    ...

    Attributes
    ----------
    width : int
        width of the image
    height : int
        height of the image
    pixels : list
        a list of RGBA objects representing pixels of the image

    Methods
    -------
    clear(r: int, g: int, b: int, a: int = 255) -> None:
        Sets all pixels to the specified color.
    save(filename: str) -> bool:
        Saves the image to a file.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        set the basic image parameters width and height and create the basic
        pixel array defaults to white
        Parameters
        ----------
            width : int
                width of the image
            height : int
                height of the image
        """
        self.width = width
        self.height = height
        self.pixels = list()
        for _ in range(width * height):
            self.pixels.append(RGBA())

    def clear(self, r: int, g: int, b: int, a: int = 255) -> None:
        """
        Sets all pixels to the specified color.

        Parameters
        ----------
            r : int
                red component of the color
            g : int
                green component of the color
            b : int
                blue component of the color
            a : int, optional
                alpha component of the color (default is 255)
        """
        for pixel in self.pixels:
            pixel.set(r, g, b, a)

    def save(self, filename: str) -> bool:
        """
        Saves the image to a file.

        Parameters
        ----------
        filename : str
            name of the file to save the image we use pillow to save the image
            and it will try and determine the file type from the extension
        """

        # build image buffer
        buffer = list()
        for pixel in self.pixels:
            buffer.append(pixel.pixel)
        image = PIL.Image.new("RGBA", (self.width, self.height), "white")
        image.putdata(buffer)

        try:
            image.save(filename)
        except IOError:
            return False
        return True

    def load(self, filename: str) -> bool:
        """
        loads in an image and stores the data into an RGBA array, note some
        truncation of data may happen here if the image is not RGBA as uint32_t formats (ie 8 bit per channel)

        Parameters
        ----------
        filename : str
            name of the file to load the image we use pillow to save the image
            and it will try and determine the file type from the extension
        """
        try:
            with PIL.Image.open(filename) as im:
                self.width = im.size[0]
                self.height = im.size[1]
                # remove old pixels if there
                self.pixels = list()
                for pixel in im.getdata():
                    self.pixels.append(RGBA(pixel[0], pixel[1], pixel[2], pixel[3]))

        except IOError:
            raise IOError
        return True

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int, a: int = 255) -> None:
        """
        Sets the color of a pixel at the specified coordinates.

        Parameters
        ----------
            x : int
                x-coordinate of the pixel
            y : int
                y-coordinate of the pixel
            r : int
                red component of the color
            g : int
                green component of the color
            b : int
                blue component of the color
            a : int, optional
                alpha component of the color (default is 255)

        Raises
        ------
            ImageXBoundsError
                If the x-coordinate is out of bounds.
            ImageYBoundsError
                If the y-coordinate is out of bounds.
        """
        if not 0 <= x <= self.width - 1:
            raise ImageXBoundsError(
                f"x index out of bounds in set_pixel {x=} {self.width=}"
            )
        if not 0 <= y <= self.height - 1:
            raise ImageYBoundsError(
                f"y index out of bounds in set_pixel {y=} {self.height=}"
            )
        offset = (y * self.width) + x
        self.pixels[offset].set(r, g, b, a)

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """
        Returns the color of a pixel at the specified coordinates.

        Parameters
        ----------
            x : int
                x-coordinate of the pixel
            y : int
                y-coordinate of the pixel

        Returns
        -------
            tuple
                A tuple containing the red, green, blue, and alpha components of the color.

        Raises
        ------
            ImageXBoundsError
                If the x-coordinate is out of bounds.
            ImageYBoundsError
                If the y-coordinate is out of bounds.
        """
        if not 0 <= x <= self.width - 1:
            raise ImageXBoundsError(
                f"x index out of bounds in get_pixel {x=} {self.width=}"
            )
        if not 0 <= y <= self.height - 1:
            raise ImageYBoundsError(
                f"y index out of bounds in get_pixel {y=} {self.height=}"
            )

        offset = (y * self.width) + x
        pixel = self.pixels[offset]
        return pixel.red(), pixel.green(), pixel.blue(), pixel.alpha()

    def get_average_rgba(self):
        average_pixel = int(sum(x.pixel for x in self.pixels) / len(self.pixels))
        new_pixel = RGBA.from_pixel(average_pixel)
        r = new_pixel.red()
        g = new_pixel.green()
        b = new_pixel.blue()
        a = new_pixel.alpha()
        return r, g, b, a

    def get_average_hsv(self):
        average_pixel = int(sum(x.pixel for x in self.pixels) / len(self.pixels))

        new_pixel = RGBA.from_pixel(average_pixel)
        h, s, v = new_pixel.as_hsv()
        return h, s, v
