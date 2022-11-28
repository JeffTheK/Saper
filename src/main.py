from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
import random

class Tile(Button):
    def __init__(self, is_bomb, **kwargs):
        super().__init__(**kwargs)
        self.is_bomb = is_bomb
        self.bind(on_press=lambda _: self.reveal())

    def reveal(self):
        if self.is_bomb:
            pass
        else:
            self.background_color = (1, 1, 1, 1)


class BoardScreen(Screen):
    tiles = []

    def setup(self, cols, rows):
        self.ids.layout.cols = cols
        self.ids.layout.rows = rows
        for x in range(cols * rows):
            tile = Tile(bool(random.getrandbits(1)))
            self.tiles.append(tile)
            self.ids.layout.add_widget(tile)

class MainScreen(Screen):
    def on_start(self, **kwargs):
        self.ids.board.setup(5, 5)

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainApp(App):
    pass

MainApp().run()