from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.config import Config
import random

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class Score:
    def __init__(self, total_tiles, bombs_count) -> None:
        self.total_tiles = total_tiles
        self.bombs_count = bombs_count
        self.cleared_tiles = 0
        self.correctly_guessed_bombs = 0

class ScoreScreen(Screen):
    score: Score = None

    def on_enter(self):
        self.ids.cleared_tiles_label.text = f"Cleared tiles: {self.score.cleared_tiles}/{self.score.total_tiles - self.score.bombs_count}"
        self.ids.correctly_guessed_bombs_label.text = f"Correctly guessed bombs: {self.score.correctly_guessed_bombs}/{self.score.bombs_count}"

class Tile(Button):
    def __init__(self, is_bomb, **kwargs):
        super().__init__(**kwargs)
        self.is_bomb = is_bomb

class BoardScreen(Screen):
    tiles = []
    nearby_bombs_colors = {
        1: (0, 0, 0, 1),
        2: (0, 0, 1, 1),
        3: (0, 1, 0, 1),
        4: (1, 0, 0, 1),
        5: (0, 0, 0, 1),
        6: (0, 0, 0, 1),
        7: (0, 0, 0, 1),
        8: (0, 0, 0, 1),
    }

    def setup(self, cols, rows, bomb_chance):
        if self.tiles != None:
            for col in self.tiles:
                for tile in col:
                    self.ids.layout.remove_widget(tile)
            self.tiles = []
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
                #tile.text = str(col) + " " + str(row)
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
        icon = Image(source="icons/flag.png", size=(tile.width / 1.5, tile.height / 1.5))
        icon.pos = (tile.x + tile.width / 2 - icon.width / 2, tile.y + tile.height / 2 - icon.height / 2)
        tile.add_widget(icon)
        if tile.is_bomb:
            self.score.correctly_guessed_bombs += 1

    def count_nearby_bombs(self, col, row) -> int:
        print("kek" + str(col) + " " + str(row))
        count = 0
        positions = [
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
            (col + 1, row + 1),
            (col - 1, row - 1),
            (col + 1, row - 1),
            (col - 1, row + 1)]
        for pos in positions:
            print(pos)
            if self.get_tile_at(pos[0], pos[1]) != None and self.get_tile_at(pos[0], pos[1]).is_bomb:
                count += 1

        return count
    
    def reveal_non_bomb_tile(self, col, row):
        tile = self.get_tile_at(col, row)
        tile.background_color = (0, 0, 0, 0)
        nearby_bombs_count = self.count_nearby_bombs(col, row)
        if (nearby_bombs_count > 0):
            tile.text = str(self.count_nearby_bombs(col, row))
            tile.color = self.nearby_bombs_colors[nearby_bombs_count]
        self.score.cleared_tiles += 1
    
    def reveal_tile(self, col, row):
        tile = self.get_tile_at(col, row)
        if tile.is_bomb:
            tile.background_color = (1, 0, 0, 1)
            tile.parent.parent.on_game_over()
        else:
            self.reveal_non_bomb_tile(col, row)

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