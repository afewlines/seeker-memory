from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

# CLASSES


class BoardGenerator():
    def __init__(self):
        self.boards = []
        self.current = -1

    def new_board(self, size, difficulty):
        board = []
        for row in range(size):
            temprow = [0 for i in range(size)]
            board.append(temprow)

        for spot in range(difficulty):
            row = randint(0, size - 1)
            col = randint(0, size - 1)
            while board[row][col] == 1:
                row = randint(0, size - 1)
                col = randint(0, size - 1)

            board[row][col] = 1

        self.boards.append(board)
        self.current += 1

    def get_board(self):
        if self.current >= 0:
            return self.boards[self.current]


# KIVY CLASSES

class Tile(ButtonBehavior, Label):
    def __init__(self, type, **kwargs):
        super(Tile, self).__init__()
        self.moniker = kwargs['index']
        self.type = type
        self.bcolor = Player.COLORS['charcoal']

    def show(self, method="DEFAULT"):
        if not method in Player.COLORS:
            method = "green"
        if self.type >= 1:
            if self.bcolor != Player.COLORS['green']:
                self.bcolor = Player.COLORS[method]
        else:
            self.bcolor = Player.COLORS['charcoal']

    def hide(self):
        self.bcolor = Player.COLORS['charcoal']

    def on_press(self):
        if Player.MANAGER.current_screen.active:
            if self.type == 1:
                print("RIGHT ", self.moniker)
                self.show()
                self.type += 1
                Player.MANAGER.current_screen.update_remaining()
                if Player.MANAGER.current_screen.remaining <= 0:
                    Player.MANAGER.current_screen.win()
            elif self.type > 1:
                pass
            else:
                print("WRONG ", self.moniker)
                Player.MANAGER.current_screen.lose()


# KIVY SCREENS

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_touch_up(self, touch):
        Player.change_screen('game')


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.grid = self.ids.grid
        self.generator = BoardGenerator()
        self.num_tiles = 11
        self.remaining = -1
        self.boardsize = 5
        self.difficulty = 2
        self.ttime = 0
        self.board = []
        self.active = False

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_pre_enter(self):
        pass

    def on_enter(self):
        # fix grid
        if self.grid.size[0] < self.grid.size[1]:
            self.grid.size_hint_y = self.grid.size[0] / self.grid.size[1]
        else:
            self.grid.size_hint_x = self.grid.size[1] / self.grid.size[0]

        # fix top bar widths
        section_width = self.ids.time.width * 0.9
        self.ids.time.text_size = [section_width, None]
        self.ids.difficulty.text_size = [section_width, None]
        self.ids.status.text_size = [section_width, None]
        # reset the board / start game
        self.reset()

    def on_leave(self):
        # put vars back to intial status
        self.board = []
        # clear grid
        self.grid.clear_widgets()

    def reset(self, args=None):
        # put vars back to intial status
        self.board = []
        self.remaining = -1
        self.ttime = 0
        self.ids.status.text = "WAIT"
        self.ids.time.text = '{0:.3f}'.format(0)
        #    self.active = False
        # clear grid
        self.grid.clear_widgets()
        # make board
        self.generator.new_board(self.boardsize, self.num_tiles)
        # get board
        self.board = self.generator.get_board()
        # update win condition
        self.remaining = self.num_tiles
        # update widgets / start game
        self.update()

    def update(self):
        # update grid
        self.ids.difficulty.text = '{0:.3f}'.format(self.difficulty)
        self.grid.clear_widgets()
        self.grid.rows = self.boardsize
        self.grid.cols = self.boardsize
        ynum = -1
        for row in self.board:
            ynum += 1
            xnum = -1
            for cell in row:
                xnum += 1
                self.grid.add_widget(
                    Tile(cell, index=(xnum, ynum)))

        Clock.schedule_once(self.start_game, 1)

    def timer(self, dt):
        if self.active:
            self.ttime += dt
            self.ids.time.text = '{0:.3f}'.format(self.ttime)
        else:
            return False

    def start_game(self, args=None):
        self.ids.status.text = "MEMORIZEc"
        for child in self.grid.children:
            child.show()
        Clock.schedule_once(self.hide_tiles, self.difficulty)

    def hide_tiles(self, args=None):
        self.ids.status.text = "{:3}".format(self.remaining)
        for child in self.grid.children:
            child.hide()
        self.active = True
        Clock.schedule_interval(self.timer, 0.01)

    def update_remaining(self):
        self.remaining -= 1
        self.ids.status.text = "{:3}".format(self.remaining)

    def win(self):
        self.active = False
        self.ids.status.text = "WIN"
        self.difficulty *= 0.92
        Clock.schedule_once(self.reset, 1)

    def lose(self):
        self.active = False
        for child in self.grid.children:
            child.show("red")
        self.ids.status.text = "LOSE"
        self.difficulty *= 1.09
        # Player.change_screen('title')
        Clock.schedule_once(self.reset, 1)


# KIVY INNARDS

class Player:
    MANAGER = ScreenManager()
    SCREENS = None
    KEY = []
    ALPHA = [lt for lt in 'abcdefghijklmnopqrswxyz1234567890 ']
    COLORS = {'brown': [0.5, 0.43, 0.27, 1],
              'offwhite': [1.0, 1.0, 0.89, 1],
              'blue': [0.29, 0.46, 0.61, 1],
              'green': [0.47, 0.60, 0.45, 1],
              'white': [1, 1, 1, 1],
              'charcoal': [0.35, 0.4, 0.43, 1],
              'red': [0.81, 0.38, 0.45, 1]}

    def __init__(self):
        Player.SCREENS = {'title': TitleScreen(name='title'),
                          'game': GameScreen(name='game')}
        for scr in Player.SCREENS:
            Player.MANAGER.add_widget(Player.SCREENS[scr])

        Player.change_screen('title')
        # self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        # self._keyboard.bind(on_key_down=self._on_keypress)

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        if Player.MANAGER.current_screen.transition_progress % 1 == 0:
            Player.MANAGER.current_screen._on_keypress(
                keyboard, keycode, text, modifiers)

    def _keyboard_closed(self):
        try:
            self._keyboard.unbind(on_key_down=self._on_keypress)
            self._keyboard = None
        except:
            pass

    @staticmethod
    def change_screen(target, *args):
        try:
            Player.MANAGER.current = target
        except:
            print('   ERROR   Screen does not exist')


class MemoryApp(App):
    def build(self):
        sm = Player()
        return sm.MANAGER


if __name__ == '__main__':
    MemoryApp().run()
