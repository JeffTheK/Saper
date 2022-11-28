from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
import random

class Tile(Button):
    def __init__(self, is_bomb, **kwargs):
        super().__init__(**kwargs)
        self.is_bomb = is_bomb

class BoardScreen(Screen):
    tiles = []

    def setup(self, cols, rows):
        self.ids.layout.cols = cols
        self.ids.layout.rows = rows
        for col in range(cols):
            self.tiles.append([])
            for row in range(rows):
                tile = Tile(bool(random.getrandbits(1)))
                tile.bind(on_press=lambda _, c=col, r=row: self.reveal_tile(c, r))
                self.tiles[col].append(tile)
                self.ids.layout.add_widget(tile)

    def count_nearby_bombs(self, col, row) -> int:
        count = 0
        positions = [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1),
        (col + 1, row + 1), (col - 1, row - 1), (col + 1, row - 1), (col - 1, row + 1)]
        for pos in positions:
            if self.get_tile_at(pos[0], pos[1]) != None and self.get_tile_at(pos[0], pos[1]).is_bomb:
                count += 1

        return count
    
    def reveal_tile(self, col, row):
        tile = self.get_tile_at(col, row)
        if tile.is_bomb:
            tile.background_color = (1, 0, 0, 1)
            tile.parent.parent.on_game_over()
        else:
            tile.background_color = (0, 0, 0, 0)
            tile.text = str(self.count_nearby_bombs(col, row))

    def get_tile_at(self, col, row) -> Tile:
        if row > self.ids.layout.rows or col > self.ids.layout.cols:
            return None
        else:
            return self.tiles[col][row]

    def on_game_over(self):
        print("GAME OVER")

class MainScreen(Screen):
    def on_start(self, **kwargs):
        self.ids.board.setup(5, 5)

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainApp(App):
    pass

MainApp().run()