Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ek79686/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/ek79686/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_EK79686/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_EK79686/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython `displayio` driver for EK79686-based ePaper displays


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-ek79686/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ek79686

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ek79686

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-ek79686

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_ek79686

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import time
    import board
    import displayio
    import fourwire
    import adafruit_ek79686

    # Used to ensure the display is free in CircuitPython
    displayio.release_displays()

    # Define the pins needed for display use on the Metro
    spi = board.SPI()
    epd_cs = board.D10
    epd_dc = board.D9
    epd_reset = board.D5
    epd_busy = board.D6

    # Create the displayio connection to the display pins
    display_bus = fourwire.FourWire(
        spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
    )
    time.sleep(1)  # Wait a bit

    # Create the display object - the third color is red (0xff0000)
    display = adafruit_ek79686.EK79686(
        display_bus,
        width=264,
        height=176,
        busy_pin=epd_busy,
        highlight_color=0xFF0000,
        rotation=90,
    )

    # Create a display group for our screen objects
    g = displayio.Group()


    # Display a ruler graphic from the root directory of the CIRCUITPY drive
    with open("/display-ruler.bmp", "rb") as f:
        pic = displayio.OnDiskBitmap(f)
        # Create a Tilegrid with the bitmap and put in the displayio group
        # CircuitPython 6 & 7 compatible
        t = displayio.TileGrid(
            pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter())
        )
        # CircuitPython 7 compatible only
        # t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
        g.append(t)

        # Place the display group on the screen (does not refresh)
        display.show(g)

        # Show the image on the display
        display.refresh()

        print("refreshed")

        # Do Not refresh the screen more often than every 180 seconds
        #   for eInk displays! Rapid refreshes will damage the panel.
        time.sleep(180)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/ek79686/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_EK79686/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
