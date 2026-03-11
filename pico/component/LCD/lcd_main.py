from machine import I2C, Pin, ADC
from pico_i2c_lcd import I2cLcd
import utime
import random

# --- CONFIGURATION ---
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
bouton = Pin(2, Pin.IN, Pin.PULL_UP) 
capteur = ADC(26) # Ton potentiomètre/capteur

# --- FONCTIONS ---
def jouer_tour(nom_joueur):
    lcd.clear()
    lcd.putstr(nom_joueur)
    lcd.move_to(0, 1)
    lcd.putstr("Appuyer pour...")
    utime.sleep(1.5)
    
    # Boucle de réglage en temps réel
    while bouton.value() == 1: 
        valeur_actuelle = int(capteur.read_u16() * 100 / 65535)
        lcd.clear()
        lcd.putstr("Reglage:")
        lcd.move_to(0, 1)
        lcd.putstr(str(valeur_actuelle) + " cm")
        utime.sleep(0.1) # Rafraîchissement rapide
    
    # Validation du clic
    lcd.clear()
    lcd.putstr("VALIDE !")
    utime.sleep(1)
    return int(capteur.read_u16() * 100 / 65535)

# --- JEU PRINCIPAL ---
CIBLE = random.randint(10, 80) # Distance secrète à atteindre

lcd.clear()
lcd.putstr("JEU A 2 JOUEURS")
lcd.move_to(0, 1)
lcd.putstr("Cible cachee !")
utime.sleep(3)

# Tour J1
val_j1 = jouer_tour("JOUEUR 1")

# Tour J2
val_j2 = jouer_tour("JOUEUR 2")

# CALCUL ET RÉSULTATS
lcd.clear()
lcd.putstr("CALCUL...")
utime.sleep(2)

diff_j1 = abs(val_j1 - CIBLE)
diff_j2 = abs(val_j2 - CIBLE)

# Affichage des scores
lcd.clear()
lcd.putstr("J1:" + str(val_j1) + "cm")
lcd.move_to(0, 1)
lcd.putstr("J2:" + str(val_j2) + "cm")
utime.sleep(4)

# Verdict
lcd.clear()
if diff_j1 < diff_j2:
    lcd.putstr("GAGNANT: J1 !")
elif diff_j2 < diff_j1:
    lcd.putstr("GAGNANT: J2 !")
else:
    lcd.putstr("EGALITE !")
    
# Affichage de la cible après le résultat
utime.sleep(2)
lcd.move_to(0, 1)
lcd.putstr("Cible etait:" + str(CIBLE))
