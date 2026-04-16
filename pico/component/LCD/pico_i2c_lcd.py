from machine import I2C, Pin
from utime import sleep_ms

# ===== CONSTANTES LCD =====
LCD_CLR             = 0x01
LCD_HOME            = 0x02
LCD_ENTRY_MODE      = 0x04
LCD_ENTRY_INC       = 0x02
LCD_ON_CTRL         = 0x08
LCD_ON_DISPLAY      = 0x04
LCD_FUNCTION        = 0x20
LCD_FUNCTION_2LINES = 0x08
LCD_SET_DDRAM       = 0x80

MASK_RS = 0x01
MASK_E  = 0x04
MASK_BL = 0x08

_ROW_OFFSETS = (0x00, 0x40)


class I2cLcd:

    def __init__(self, i2c, addr, num_lines=2, num_columns=16):
        self.i2c = i2c
        self.addr = addr
        self.backlight = MASK_BL

        sleep_ms(50)

        self._write_cmd(0x03)
        sleep_ms(5)
        self._write_cmd(0x03)
        sleep_ms(5)
        self._write_cmd(0x03)
        sleep_ms(5)
        self._write_cmd(0x02)

        self._write_cmd(LCD_FUNCTION | LCD_FUNCTION_2LINES)
        self._write_cmd(LCD_ON_CTRL | LCD_ON_DISPLAY)
        self.clear()
        self._write_cmd(LCD_ENTRY_MODE | LCD_ENTRY_INC)

    def _write_byte(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.backlight]))

    def _pulse(self, data):
        self._write_byte(data | MASK_E)
        sleep_ms(1)
        self._write_byte(data & ~MASK_E)
        sleep_ms(1)

    def _write_cmd(self, cmd):
        high = cmd & 0xF0
        low  = (cmd << 4) & 0xF0
        self._write_byte(high)
        self._pulse(high)
        self._write_byte(low)
        self._pulse(low)

    def _write_data(self, data):
        high = (data & 0xF0) | MASK_RS
        low  = ((data << 4) & 0xF0) | MASK_RS
        self._write_byte(high)
        self._pulse(high)
        self._write_byte(low)
        self._pulse(low)

    def clear(self):
        self._write_cmd(LCD_CLR)
        sleep_ms(2)

    def move_to(self, col, row):
        self._write_cmd(LCD_SET_DDRAM | (_ROW_OFFSETS[row] + col))

    def putstr(self, text):
        for ch in text:
            self._write_data(ord(ch))

