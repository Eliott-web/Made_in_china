from machine import Pin, Timer
import _thread
import time

# Pins pour le 4511 (A LSB, B, C, D MSB)
A = Pin(10, Pin.OUT)
B = Pin(11, Pin.OUT)
C = Pin(12, Pin.OUT)
D = Pin(13, Pin.OUT)

# Transistors pour activer chaque afficheur
segUnit = Pin(14, Pin.OUT)
segDiz = Pin(15, Pin.OUT)

# Variable globale qui s'incrémente
valeur = 0


# Affiche un chiffre (0-9) sur le 4511
def output_digit(digit):
    global A, B, C, D
    bin_str = f'{int(digit):04b}'
    A.value(int(bin_str[-1]))
    B.value(int(bin_str[-2]))
    C.value(int(bin_str[-3]))
    D.value(int(bin_str[-4]))


# Thread d'affichage multiplexé
def display_thread():
    global valeur, segUnit, segDiz

    segUnit.value(0)
    segDiz.value(0)

    while True:
        unit = valeur % 10
        diz = valeur // 10

        # Affiche unité
        output_digit(unit)
        segUnit.value(1)
        time.sleep_ms(5)
        segUnit.value(0)

        # Affiche dizaine
        output_digit(diz)
        segDiz.value(1)
        time.sleep_ms(5)
        segDiz.value(0)


# Fonction incrémentation valeur
def change_valeur(timer):
    global valeur
    valeur += 1
    if valeur >= 100:
        valeur = 0


def init():
    _thread.start_new_thread(display_thread, ())  # Lancer le thread d'affichage

    timer = Timer()
    timer.init(freq=1, mode=Timer.PERIODIC, callback=change_valeur)


def main_loop():
    while True:
        pass


init()
main_loop()
