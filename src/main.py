from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.config import Config
from kivy.clock import Clock
import random
import datetime

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# структура яка містить статистику гравця після перемоги/програшу
class Score:
    def __init__(self, total_tiles, bombs_count) -> None:
        self.total_tiles = total_tiles
        self.bombs_count = bombs_count
        self.cleared_tiles = 0
        self.correctly_guessed_bombs = 0

# Годинник який показує скільки пройшло часу з початку гри
class Timer(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.datetime.now()
        Clock.schedule_interval(lambda _: self.update(), 1)

    # Оновлює інтерфейс    
    def update(self):
        self.elapsed_time = datetime.datetime.now() - self.start_time
        s = self.elapsed_time.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.text = '{:02}:{:02}'.format(int(minutes), int(seconds))

    # Перезапускає годинник    
    def start(self):
        self.start_time = datetime.datetime.now()
        self.text = "00:00"

# Клас екрану резулбтату гри
class ScoreScreen(Screen):
    score: Score = None

    def on_enter(self):
        self.ids.cleared_tiles_label.text = f"Cleared tiles: {self.score.cleared_tiles}/{self.score.total_tiles - self.score.bombs_count}"
        self.ids.correctly_guessed_bombs_label.text = f"Correctly guessed bombs: {self.score.correctly_guessed_bombs}/{self.score.bombs_count}"

# Комірка яка може містити бомбу
class Tile(Button):
    def __init__(self, is_bomb, **kwargs):
        super().__init__(**kwargs)
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.is_revealed = False

# Основний клас де відбувається гра. 
# Контролює сітку з полями
class BoardScreen(Screen):
    tiles = []

    # кольори залежно скільки бомб біля комірки
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

    # Налаштовує сітку з комірками
    def setup(self, cols, rows, bomb_chance):
        if self.tiles != None:
            for col in self.tiles:
                for tile in col:
                    self.ids.layout.remove_widget(tile)
            self.tiles = []
        self.ids.layout.cols = cols
        self.ids.layout.rows = rows
        self.ids.timer.start()
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

    # Викликається коли гравець натискає на комірку
    # Саме перевіряє яка з кнопок миші була натиснута
    def on_tile_touch_down(self, col, row, touch):
        tile = self.get_tile_at(col, row)
        if not tile.collide_point(*touch.pos):
            return

        if touch.button == "left":
            self.reveal_tile(col, row)
        elif touch.button == "right":
            self.flag_tile(col ,row)

    # Ставить/видаляє флаг на комірці
    def flag_tile(self, col, row):
        tile = self.get_tile_at(col, row)

        if tile.is_revealed:
            return

        if tile.is_flagged:
            tile.is_flagged = False
            tile.remove_widget(tile.icon)
            if tile.is_bomb:
                self.score.correctly_guessed_bombs -= 1
        else:
            tile.is_flagged = True
            icon = Image(source="icons/flag.png", size=(tile.width / 1.5, tile.height / 1.5))
            icon.pos = (tile.x + tile.width / 2 - icon.width / 2, tile.y + tile.height / 2 - icon.height / 2)
            tile.icon = icon
            tile.add_widget(icon)
            if tile.is_bomb:
                self.score.correctly_guessed_bombs += 1

    # Повертає кількість сусідніх комірок з бомбами
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
    
    # Викликається якщо натиснута комірка не має бомб.
    # Рекурсивно викликається на сусідах
    def reveal_non_bomb_tile(self, col, row):
        positions = [
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
        ]

        tile = self.get_tile_at(col, row)
        if tile.is_bomb or tile.is_revealed:
            return

        tile.is_revealed = True
        tile.background_color = (0, 0, 0, 0)
        nearby_bombs_count = self.count_nearby_bombs(col, row)
        if (nearby_bombs_count > 0):
            tile.text = str(self.count_nearby_bombs(col, row))
            tile.color = self.nearby_bombs_colors[nearby_bombs_count]
        else:
            for pos in positions:
                if self.get_tile_at(pos[0], pos[1]) != None:
                    self.reveal_non_bomb_tile(pos[0], pos[1])
        self.score.cleared_tiles += 1
    
    # Викликається коли гравець натиснув і хоче відкрити комірку
    def reveal_tile(self, col, row):
        tile = self.get_tile_at(col, row)
        if tile.is_bomb:
            tile.background_color = (1, 0, 0, 1)
            App.get_running_app().root.get_screen("board").on_game_over()
            tile.is_revealed = True
        else:
            self.reveal_non_bomb_tile(col, row)

    def get_tile_at(self, col, row) -> Tile:
        if row > self.ids.layout.rows - 1 or col > self.ids.layout.cols - 1 or row < 0 or col < 0:
            return None
        else:
            return self.tiles[col][row]

    # Викликається при поразці
    def on_game_over(self):
        App.get_running_app().root.get_screen("score").score = self.score
        App.get_running_app().root.current = "score"

# Перший екран
class MainScreen(Screen):
    pass

# Керує всіма так званими екранами (Screen)
class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainApp(App):
    pass

MainApp().run()