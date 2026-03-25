import random

rounds = []


class Round:

    _ANNOUNCE    = 0
    _PLAYER_TURN = 1
    _CONFIRM     = 2
    _RESULT      = 3
    _DONE        = 4

    def __init__(self, lcd, sensor, button, round_number):
        global rounds
        self.lcd = lcd
        self.sensor = sensor
        self.button = button
        self.round_number = round_number
        self.target = random.randint(10, 150)
        self._state = self._ANNOUNCE
        self._current_player = 1
        self._distances = [0.0, 0.0]
        self._prev_btn = 1
        self._needs_redraw = True
        rounds.append(self)
        self.active = True

    def _measure(self):
        try:
            return round(self.sensor.distance_cm(), 1)
        except OSError:
            return -1.0

    def _btn_released(self):
        val = self.button.value()
        released = self._prev_btn == 0 and val == 1
        self._prev_btn = val
        return released

    def compute_winner(self):
        diff1 = abs(self._distances[0] - self.target)
        diff2 = abs(self._distances[1] - self.target)
        if diff1 < diff2:
            return 1
        if diff2 < diff1:
            return 2
        return 0

    def _draw_announce(self):
        self.lcd.clear()
        self.lcd.putstr("Round " + str(self.round_number))
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Cible: " + str(self.target) + " cm")

    def _draw_player_turn(self, dist):
        self.lcd.clear()
        self.lcd.putstr("J" + str(self._current_player) + ": " + str(dist) + " cm")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Cible: " + str(self.target) + " cm")

    def _draw_confirm(self):
        self.lcd.clear()
        self.lcd.putstr("J" + str(self._current_player) + ": " + str(self._distances[self._current_player - 1]) + " cm")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("OK -> appuyer")

    def _draw_result(self, winner):
        self.lcd.clear()
        if winner == 0:
            self.lcd.putstr("Egalite !")
        else:
            self.lcd.putstr("Gagnant: J" + str(winner) + " !")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Cible: " + str(self.target) + " cm")

    def loop(self):
        released = self._btn_released()

        if self._state == self._ANNOUNCE:
            if self._needs_redraw:
                self._draw_announce()
                self._needs_redraw = False
            if released:
                self._state = self._PLAYER_TURN
                self._needs_redraw = True

        elif self._state == self._PLAYER_TURN:
            dist = self._measure()
            self._draw_player_turn(dist)
            if released:
                self._distances[self._current_player - 1] = dist
                self._state = self._CONFIRM
                self._needs_redraw = True

        elif self._state == self._CONFIRM:
            if self._needs_redraw:
                self._draw_confirm()
                self._needs_redraw = False
            if released:
                if self._current_player == 1:
                    self._current_player = 2
                    self._state = self._PLAYER_TURN
                else:
                    self._state = self._RESULT
                self._needs_redraw = True

        elif self._state == self._RESULT:
            if self._needs_redraw:
                self._draw_result(self.compute_winner())
                self._needs_redraw = False
            if released:
                self._state = self._DONE

        elif self._state == self._DONE:
            self.active = False
            return self.compute_winner()

        return None
