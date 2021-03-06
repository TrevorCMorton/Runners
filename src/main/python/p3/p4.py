import os.path
import p3.memory_watcher
import p3.menu_manager
import p3.pad
import p3.state
import p3.state_manager
import p3.screen_watcher
import numpy as np
import cv2
from threading import Semaphore, Thread
import time
from subprocess import call
import PIL
import scipy.misc
import time

class P4:
    def __init__(self, setup, size, depth, save_hits):
        self.setup = setup
        self.selected_fox = False
        self.selected_cpu = False
        self.setup_cpu = False
        self.sw = None
        self.dolphin_dir = None
        self.reward = 0
        self.players = []
        self.post_game = False
        self.restarting = False
        self.frame = None
        self.cpu_level = 3
        self.window_selected = False
        self.size = size
        self.save_hits = save_hits
        self.save_buffer = [None] * depth
        self.frame_buffer = [np.zeros(size * size)] * depth
        self.game_state = [[0] * (13 * 2)] * depth
        self.actionMasks = [0] * 26
        self.num_to_gather = 4
        self.num_gathered = 0
        self.lock = Semaphore(1)
        self.gathered = Semaphore(0)
        self.gathering = Semaphore(depth)
        self.total_gathered = 0


    def find_dolphin_dir(self):
        """Attempts to find the dolphin user directory. None on failure."""
        candidates = ['~/Runners/.dolphin-emu', '/home/Runners/.dolphin-emu']
        for candidate in candidates:
            path = os.path.expanduser(candidate)
            if os.path.isdir(path):
                return path
        return None

    def write_locations(self, dolphin_dir, locations):
        """Writes out the locations list to the appropriate place under dolphin_dir."""
        path = dolphin_dir + '/MemoryWatcher/Locations.txt'
        with open(path, 'w') as f:
            f.write('\n'.join(locations))

            dolphin_dir = self.find_dolphin_dir()
            if dolphin_dir is None:
                print('Could not detect dolphin directory.')
                return

    def run(self, state, sm, mw, pad):
        mm = p3.menu_manager.MenuManager()
        result = False
        while not result:
            last_frame = state.frame
            res = next(mw)
            if res is not None:
                sm.handle(*res)
            if state.frame > last_frame:
                result = self.make_action(state, pad, mm)

    def make_action(self, state, pad, mm):
        if state.menu == p3.state.Menu.Game:
            pad.reset()
            return True
        elif state.menu == p3.state.Menu.Characters:
            if self.setup:
                if mm.pick_cpu(state, pad):
                    if mm.pick_dk(state, pad):
                        if mm.set_rules(state, pad):
                            if mm.set_level(state, pad, self.cpu_level):
                                mm.press_start_lots(state, pad)
            else:
                if mm.pick_kirby(state, pad):
                    return False
            return False
        elif state.menu == p3.state.Menu.Stages:
            if not self.window_selected:
                call(["wmctrl", "-a", "FPS"])
                self.window_selected = True
            if mm.pick_map(state, pad):
                mm.press_start_lots(state, pad)
            return False
        elif state.menu == p3.state.Menu.PostGame:
            mm.press_start_lots(state, pad)
            return False

    def start(self):
        self.dolphin_dir = self.find_dolphin_dir()
        if self.dolphin_dir is None:
            print('Could not find dolphin config dir.')
            return

        if self.cpu_level == 0:
            self.cpu_level = np.random.choice(range(1, 10))

        game_state = p3.state.State()
        sm = p3.state_manager.StateManager(game_state)
        self.write_locations(self.dolphin_dir, sm.locations())

        pad_path = self.dolphin_dir + '/Pipes/p3'
        mw_path = self.dolphin_dir + '/MemoryWatcher/MemoryWatcher'
        with p3.pad.Pad(pad_path) as pad, p3.memory_watcher.MemoryWatcher(mw_path) as mw:
            self.run(game_state, sm, mw, pad)
        self.sw = p3.screen_watcher.ScreenWatcher()
        thread = Thread(target=self.frame_reward)
        thread.start()

    def is_post_game(self):
        return self.post_game

    def get_frame_reward(self):
        temp = self.reward
        self.reward = 0

        if self.save_hits and temp != 0 and self.save_buffer[3] is not None:
            file_time = time.time()
            for i in range(0, len(self.save_buffer)):
                file_name = str(file_time) + "_" + str(i) + ".png"
                scipy.misc.imsave(file_name, self.save_buffer[i])
        #if temp == 0:
        #    temp += .05
        return temp

    def frame_reward(self):
        game_state = p3.state.State()
        sm = p3.state_manager.StateManager(game_state)
        mw_path = self.dolphin_dir + '/MemoryWatcher/MemoryWatcher'
        mm = p3.menu_manager.MenuManager()
        with p3.memory_watcher.MemoryWatcher(mw_path) as mw:
            while True:

                last_frame = game_state.frame
                res = next(mw)
                if res is not None:
                    sm.handle(*res)
                if game_state.frame > last_frame:
                    self.gathering.acquire()

                    self.frame = self.get_frame(self.size)

                    if game_state.menu == p3.state.Menu.PostGame:
                        self.post_game = True
                    elif game_state.menu == p3.state.Menu.Game:
                        self.post_game = False

                    if self.post_game:
                        pad_path = self.dolphin_dir + '/Pipes/p3'
                        with p3.pad.Pad(pad_path) as pad:
                            mm.press_start_lots(game_state, pad)

                    i = 0
                    players = game_state.players
                    players_tuples = []
                    while i < len(players):
                        tuple = (players[i].percent, players[i].stocks)
                        if len(self.players) != 0:
                            if i == 2:
                                if self.players[i][0] < tuple[0]:
                                    self.reward -= .1
                                    #self.reward -= 1
                                if self.players[i][1] != tuple[1]:
                                    self.reward -= 1
                            else:
                                if self.players[i][0] < tuple[0]:
                                    self.reward += .1
                                    #self.reward += 1
                                if self.players[i][1] != tuple[1]:
                                    self.reward += 1
                        i += 1
                        players_tuples.append(tuple)
                    self.players = players_tuples

                    totalState = []

                    for i in (1, 2):
                        #totalState.append(float(game_state.players[i].action_state.value))
                        totalState.append(float(game_state.players[i].self_air_vel_x) / 100)
                        totalState.append(float(game_state.players[i].self_air_vel_y) / 100)
                        totalState.append(float(game_state.players[i].attack_vel_x) / 100)
                        totalState.append(float(game_state.players[i].attack_vel_y) / 100)
                        totalState.append(float(game_state.players[i].pos_x) / 250)
                        totalState.append(float(game_state.players[i].pos_y) / 250)
                        totalState.append(float(game_state.players[i].on_ground))
                        totalState.append(float(game_state.players[i].percent) / 100)
                        totalState.append(float(game_state.players[i].hitlag) / 100)
                        totalState.append(float(game_state.players[i].hitstun) / 100)
                        totalState.append(float(game_state.players[i].jumps_used) / 100)
                        #totalState.append(float(game_state.players[i].body_state.value))
                        totalState.append(float(game_state.players[i].shield_size) / 100)
                        totalState.append(float(game_state.players[i].facing))

                    for i in range(0, len(self.game_state)):
                        temp = self.game_state[i]
                        self.game_state[i] = totalState
                        totalState = temp

                    self.total_gathered += 1

                    self.lock.acquire()
                    self.num_gathered += 1
                    if self.num_gathered == self.num_to_gather:
                        self.lock.release()
                        self.gathered.release()
                    else:
                        self.lock.release()

    def get_state(self):
        self.gathered.acquire()

        self.lock.acquire()
        self.num_gathered = 0
        self.lock.release()

        state = []

        for i in range(0, len(self.game_state)):
            state += self.game_state[i]

        for i in range(0, self.num_to_gather):
            self.gathering.release()

        return state + self.actionMasks


    def get_frame(self, size):
        screen = next(self.sw)

        to_update = np.array(screen)[:, :, :3]
        for i in range(0, len(self.save_buffer)):
            temp = self.save_buffer[i]
            self.save_buffer[i] = to_update
            to_update = temp

        frame = self.to_grayscale(cv2.resize(np.array(screen), (size, size), interpolation=cv2.INTER_AREA)).flatten(order='C')

        to_update = frame
        for i in range(0, len(self.frame_buffer)):
            temp = self.frame_buffer[i]
            self.frame_buffer[i] = to_update
            to_update = temp

        return np.concatenate(self.frame_buffer) / 255

    def get_frame_fast(self):
        self.gathered.acquire()

        self.lock.acquire()
        self.num_gathered = 0
        self.lock.release()

        for i in range(0, self.num_to_gather):
            self.gathering.release()

        return self.frame

    def get_flat_frame(self):
        screen = self.get_frame_fast()
        return screen#.flatten()

    def to_grayscale(self, image):
        return np.dot(image[..., :3], [0.114, 0.587, 0.299]) # image is in bgra

    def execute(self, actions):
        pad_path = self.dolphin_dir + '/Pipes/p3'
        actionMasks = [0] * 26
        with p3.pad.Pad(pad_path) as pad:
            for actionSet in actions:
                for action in actionSet.split(':'):
                    if action == 'MR':
                        pad.tilt_stick(p3.pad.Stick.MAIN, .5, .5)
                        actionMasks[0] = 1
                    elif action == 'MN':
                        pad.tilt_stick(p3.pad.Stick.MAIN, .5, 1)
                        actionMasks[1] = 1
                    elif action == 'MNW':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 1, 1)
                        actionMasks[2] = 1
                    elif action == 'MW':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 1, .5)
                        actionMasks[3] = 1
                    elif action == 'MSW':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 1, 0)
                        actionMasks[4] = 1
                    elif action == 'MS':
                        pad.tilt_stick(p3.pad.Stick.MAIN, .5, 0)
                        actionMasks[5] = 1
                    elif action == 'MSE':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 0, 0)
                        actionMasks[6] = 1
                    elif action == 'ME':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 0, .5)
                        actionMasks[7] = 1
                    elif action == 'MNE':
                        pad.tilt_stick(p3.pad.Stick.MAIN, 0, 1)
                        actionMasks[8] = 1

                    if action == 'CR':
                        pad.tilt_stick(p3.pad.Stick.C, .5, .5)
                        actionMasks[9] = 1
                    elif action == 'CN':
                        pad.tilt_stick(p3.pad.Stick.C, .5, 1)
                        actionMasks[10] = 1
                    elif action == 'CNW':
                        pad.tilt_stick(p3.pad.Stick.C, 1, 1)
                        actionMasks[11] = 1
                    elif action == 'CW':
                        pad.tilt_stick(p3.pad.Stick.C, 1, .5)
                        actionMasks[12] = 1
                    elif action == 'CSW':
                        pad.tilt_stick(p3.pad.Stick.C, 1, 0)
                        actionMasks[13] = 1
                    elif action == 'CS':
                        pad.tilt_stick(p3.pad.Stick.C, .5, 0)
                        actionMasks[14] = 1
                    elif action == 'CSE':
                        pad.tilt_stick(p3.pad.Stick.C, 0, 0)
                        actionMasks[15] = 1
                    elif action == 'CE':
                        pad.tilt_stick(p3.pad.Stick.C, 0, .5)
                        actionMasks[16] = 1
                    elif action == 'CNE':
                        pad.tilt_stick(p3.pad.Stick.C, 0, 1)
                        actionMasks[17] = 1

                    if action == 'PA':
                        pad.press_button(p3.pad.Button.A)
                        actionMasks[18] = 1
                    elif action == 'RA':
                        pad.release_button(p3.pad.Button.A)
                        actionMasks[19] = 1

                    if action == 'PB':
                        pad.press_button(p3.pad.Button.B)
                        actionMasks[20] = 1
                    elif action == 'RB':
                        pad.release_button(p3.pad.Button.B)
                        actionMasks[21] = 1

                    if action == 'PY':
                        pad.press_button(p3.pad.Button.Y)
                        actionMasks[22] = 1
                    elif action == 'RY':
                        pad.release_button(p3.pad.Button.Y)
                        actionMasks[23] = 1

                    if action == 'PZ':
                        pad.press_button(p3.pad.Button.Z)
                        actionMasks[24] = 1
                    elif action == 'RZ':
                        pad.release_button(p3.pad.Button.Z)
                        actionMasks[25] = 1

        self.actionMasks = actionMasks
