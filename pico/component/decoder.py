from machine import Pin, Timer

# Pins BCD pour le 4511 (A=LSB, D=MSB)
A = Pin(10, Pin.OUT)
B = Pin(11, Pin.OUT)
C = Pin(12, Pin.OUT)
D = Pin(13, Pin.OUT)

# Transistors : seg1 = afficheur J1, seg2 = afficheur J2
seg1 = Pin(14, Pin.OUT)
seg2 = Pin(15, Pin.OUT)

score1 = 0
score2 = 0
_phase = 0
_timer = Timer()


def set_scores(s1, s2):
    global score1, score2
    score1 = s1
    score2 = s2


def _output_digit(digit):
    digit = max(0, min(9, int(digit)))
    bin_str = '{:04b}'.format(digit)
    A.value(int(bin_str[-1]))
    B.value(int(bin_str[-2]))
    C.value(int(bin_str[-3]))
    D.value(int(bin_str[-4]))


def _tick(t):
    global _phase
    seg1.value(0)
    seg2.value(0)
    if _phase == 0:
        _output_digit(score1)
        seg1.value(1)
    else:
        _output_digit(score2)
        seg2.value(1)
    _phase ^= 1


def start():
    _timer.init(mode=Timer.PERIODIC, period=5, callback=_tick)


def stop():
    _timer.deinit()
    seg1.value(0)
    seg2.value(0)
