class SevenSegments:
    """Driver for a single 7‑segment display attached to a Raspberry Pi Pico.

    The display is assumed to be common cathode.  The constructor accepts
    either raw pin numbers or :class:`machine.Pin` objects in the order
    ``a, b, c, d, e, f, g`` (optionally followed by ``dp`` for the decimal
    point).  Each segment is then configured as an output pin.

    ``display()`` takes an integer 0–9 (or any key present in
    ``SEGMENTS``) and lights the appropriate segments.  The implementation
    also exposes lower‑level helpers for clearing the display and directly
    setting the segment states.  This keeps the high‑level logic in one
    place and makes it easy to add new characters later.
    """

    # order of pins in the tuple used internally
    _SEGMENT_ORDER = ("a", "b", "c", "d", "e", "f", "g", "dp")

    # mapping of characters to segment states (1 == on, 0 == off)
    SEGMENTS = {
        0: (1, 1, 1, 1, 1, 1, 0),
        1: (0, 1, 1, 0, 0, 0, 0),
        2: (1, 1, 0, 1, 1, 0, 1),
        3: (1, 1, 1, 1, 0, 0, 1),
        4: (0, 1, 1, 0, 0, 1, 1),
        5: (1, 0, 1, 1, 0, 1, 1),
        6: (1, 0, 1, 1, 1, 1, 1),
        7: (1, 1, 1, 0, 0, 0, 0),
        8: (1, 1, 1, 1, 1, 1, 1),
        9: (1, 1, 1, 1, 0, 1, 1),
    }

    def __init__(self, *pins):
        # pins may be integers or Pin objects; convert them all
        from machine import Pin

        if not (7 <= len(pins) <= 8):
            raise ValueError("Expected 7 or 8 pin values (a..g[,dp])")

        # create a dict mapping segment name -> Pin object
        self._pins = {}
        for name, p in zip(self._SEGMENT_ORDER, pins):
            if isinstance(p, Pin):
                pin_obj = p
            else:
                pin_obj = Pin(p, Pin.OUT)
            self._pins[name] = pin_obj

        # if decimal point wasn't provided, leave it as None
        if len(pins) == 7:
            self._pins["dp"] = None

        # start cleared
        self.clear()

    def clear(self):
        """Turn all segments (and decimal point) off."""
        for pin in self._pins.values():
            if pin is not None:
                pin.value(0)

    def set_segments(self, pattern, dp=False):
        """Set the raw segment pattern.

        ``pattern`` should be an iterable of seven booleans or ints matching
        ``a,b,c,d,e,f,g``.  ``dp`` controls the decimal point if it was
        configured.
        """
        for name, state in zip(self._SEGMENT_ORDER, pattern + (dp,)):
            pin = self._pins.get(name)
            if pin is not None:
                pin.value(1 if state else 0)

    def display(self, number, dp=False):
        """Display a single digit (0-9) or other supported key.

        ``number`` may be an integer or any key present in :data:`SEGMENTS`.
        ``dp`` enables the decimal point if available.
        """
        pattern = self.SEGMENTS.get(number)
        if pattern is None:
            raise ValueError(f"Character {number!r} not supported")
        self.set_segments(pattern, dp)