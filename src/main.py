from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
import random

class Score:
    def __init__(self, total_tiles, bombs_count) -> None:
        self.total_tiles = total_tiles
        self.bombs_count = bombs_count
        self.cleared_tiles = 0
        self.correctly_guessed_bombs = 0

class ScoreScreen(Screen):
    score: Score = None

    def on_enter(self):
        self.ids.cleared_tiles_label.text += f" {self.score.cleared_tiles}/{self.score.total_tiles - self.score.bombs_count}"
        self.ids.correctly_guessed_bombs_label.text += f" {self.score.correctly_guessed_bombs}/{self.score.bombs_count}"

class Tile(Button):
    def __init__(self, is_bomb, **kwargs):
        super().__init__(**kwargs)
        self.is_bomb = is_bomb

class BoardScreen(Screen):
    tiles = []

    def setup(self, cols, rows, bomb_chance):
        self.ids.layout.cols = cols
        self.ids.layout.rows = rows
        self.bomb_chance = bomb_chance
        bombs_count = 0
        for col in range(cols):
            self.tiles.append([])
            for row in range(rows):
                is_bomb = random.randrange(0, 100) <= self.bomb_chance
                if is_bomb:
                    bombs_count += 1
                tile = Tile(is_bomb)
                tile.bind(on_touch_down=lambda _, touch, c=col, r=row: self.on_tile_touch_down(c, r, touch))
                self.tiles[col].append(tile)
                self.ids.layout.add_widget(tile)
        self.score = Score(cols * rows, bombs_count)

    def on_tile_touch_down(self, col, row, touch):
        tile = self.get_tile_at(col, row)
        if not tile.collide_point(*touch.pos):
            return

        if touch.button == "left":
            self.reveal_tile(col, row)
        elif touch.button == "right":
            self.flag_tile(col ,row)

    def flag_tile(self, col, row):
        tile = self.get_tile_at(col, row)
        if tile.is_bomb:
            self.score.correctly_guessed_bombs += 1

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
            self.score.cleared_tiles += 1

    def get_tile_at(self, col, row) -> Tile:
        if row > self.ids.layout.rows - 1 or col > self.ids.layout.cols - 1:
            return None
        else:
            return self.tiles[col][row]

    def on_game_over(self):
        App.get_running_app().root.get_screen("score").score = self.score
        App.get_running_app().root.current = "score"

class MainScreen(Screen):
    pass

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainApp(App):
    pass

MainApp().run()