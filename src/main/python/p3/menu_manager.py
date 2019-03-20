import math
from numpy import random

import p3.pad

class MenuManager:
    def __init__(self):
        self.selected_fox = False
        self.selected_cpu = False
        self.setup_cpu = False
        self.entered_menu = False
        self.rules_set = True
        self.menu_count = 0
        self.start_frame = -1
        self.map_frames = 0
        self.map_moves = 0
        self.clicked_level = False
        self.picked_level = False

    def set_rules(self, state, pad):
        if self.rules_set:
            pad.release_button(p3.pad.Button.B)
            return True
        if self.entered_menu:
            pad.release_button(p3.pad.Button.A)
            if self.menu_count == 0:
                if self.start_frame == -1:
                    self.start_frame = state.frame
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, 0)
            if self.menu_count == 1:
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            if self.menu_count == 2:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0, .5)
            if self.menu_count == 3:
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            if self.menu_count == 4:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0, .5)
            if self.menu_count == 5:
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            if self.menu_count == 6:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0, .5)
            if self.menu_count == 7:
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            if self.menu_count == 8:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0, .5)
            if self.menu_count == 9:
                pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            if self.menu_count == 10:
                pad.press_button(p3.pad.Button.B)
                self.rules_set = True
            if state.frame - self.start_frame > 20:
                self.menu_count += 1
            return False
        else:
            # Go to cpu and press A
            target_x = -15.5
            target_y = 22
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 0.35:
                pad.press_button(p3.pad.Button.A)
                self.entered_menu = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False

    def pick_cpu(self, state, pad):
        if self.setup_cpu:
            return True
        if self.selected_cpu:
            # Release buttons and lazilly rotate the c stick.
            pad.release_button(p3.pad.Button.A)
            self.setup_cpu = True
            return False
        else:
            # Go to cpu and press A
            target_x = -15.5
            target_y = -4.0
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 0.35:
                pad.press_button(p3.pad.Button.A)
                self.selected_cpu = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False

    def pick_fox(self, state, pad):
        if self.selected_fox:
            pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            pad.release_button(p3.pad.Button.A)
            return True
        else:
            # Go to fox and press A
            target_x = -23.5
            target_y = 11.5
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 1:
                pad.press_button(p3.pad.Button.A)
                self.selected_fox = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False

    def pick_kirby(self, state, pad):
        if self.selected_fox:
            pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            pad.release_button(p3.pad.Button.A)
            return True
        else:
            # Go to kirby and press A
            target_x = -3
            target_y = 11.5
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 1:
                pad.press_button(p3.pad.Button.A)
                self.selected_fox = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False

    def pick_dk(self, state, pad):
        if self.selected_fox:
            pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
            pad.release_button(p3.pad.Button.A)
            return True
        else:
            # Go to kirby and press A
            target_x = 8
            target_y = 20
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 1:
                pad.press_button(p3.pad.Button.A)
                self.selected_fox = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False

    def set_level(self, state, pad, level):
        if self.picked_level:
            pad.release_button(p3.pad.Button.A)
            return True
        elif self.clicked_level:
            # move cursor proper amount
            target_x = -15.5 + (level - 1)
            target_y = -15
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < .7:
                pad.press_button(p3.pad.Button.A)
                self.picked_level = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False
        else:
            # Go to level selector and press A
            target_x = -15.5
            target_y = -15
            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 1:
                pad.press_button(p3.pad.Button.A)
                self.clicked_level = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)
            return False


    def pick_map(self, state, pad):
        if self.map_moves < 20 and self.map_frames % 10 == 0:
            pad.tilt_stick(p3.pad.Stick.MAIN, .6, .7)
            self.map_moves += 1
        else:
            pad.reset()
        self.map_frames += 1
        if self.map_moves >= 15:
            return True

    def press_start_lots(self, state, pad):
        if state.frame % 2 == 0:
            pad.press_button(p3.pad.Button.START)
        else:
            pad.release_button(p3.pad.Button.START)
