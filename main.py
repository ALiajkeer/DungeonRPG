import random
import pygame
import tkinter as tk
import sqlite3

# フォント
FONT_SIZE = 24
FONT_PATH = "font/Corporate-Mincho-ver3.otf"

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 225, 0)
GREEN = (0, 225, 0)

# ダンジョンの広さ
DUNGEON_SIZE = 1000
DUNGEON_WIDTH = 85
DUNGEON_HEIGHT = 80
DISP_SPACE = 50

PLAYER_DB = 'player_data.db'

DEFAULT_HP = 100
DEFAULT_MP = 100


class Player:
    def __init__(self, hp, mp):
        self.max_hp = hp
        self.max_mp = mp
        self.HP = self.max_hp
        self.MP = self.max_mp


class Dungeon:
    def __init__(self, width, height):
        # 日本語フォント設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)

        self.width = width
        self.height = height
        self.layer = 1
        self.player_pos = [0, 0]
        self.enemy_pos = [0, 0]
        self.dungeon_size = [[0, 0], [0, 0]]
        self.movable_area = []
        self.screen = pygame.display.set_mode((width * 10, height * 10))
        self.player_data = Player(DEFAULT_HP, DEFAULT_MP)

    # ダンジョンの生成(ダンジョン初期設定)
    def generate_dungeon(self):
        # 移動可能領域の初期化
        self.movable_area.clear()

        self.dungeon_size = [[0 for _ in range(self.height)] for _ in range(self.width)]
        x, y = int(self.width / 2), int(self.height / 2)
        self.dungeon_size[x][y] = 1

        # ダンジョン生成
        for i in range(DUNGEON_SIZE):
            direction = random.randint(1, 4)
            if direction == 1 and x > 1:
                x -= 1
            elif direction == 2 and x < self.width - 2:
                x += 1
            elif direction == 3 and y > 1:
                y -= 1
            elif direction == 4 and y < self.height - 2:
                y += 1
            self.dungeon_size[x][y] = 1

        # プレイヤー生成
        # ダンジョン内で白色の部分を探す
        for i in range(len(self.dungeon_size)):
            for j in range(len(self.dungeon_size[0])):
                # 移動可能領域の場合
                if self.dungeon_size[i][j] == 1:
                    # 移動可能領域の座標を格納
                    self.movable_area.append([j, i])

        # 下層移動オブジェクトを配置する
        selected_cell = random.choice(self.movable_area)
        self.dungeon_size[selected_cell[1]][selected_cell[0]] = 2

        # 回復の泉オブジェクトを50%の確率で配置する
        if random.random() < 0.5:
            selected_cell = random.choice(self.movable_area)
            self.dungeon_size[selected_cell[1]][selected_cell[0]] = 3

        # プレイヤーを配置する
        selected_cell = random.choice(self.movable_area)
        self.player_pos = [selected_cell[1], selected_cell[0]]

        # 敵オブジェクトを配置する
        selected_cell = random.choice(self.movable_area)
        self.enemy_pos = [selected_cell[1], selected_cell[0]]

    # ダンジョンの描画
    def draw_dungeon(self):
        # # 日本語フォント設定
        # font = pygame.font.Font("font/Corporate-Mincho-ver3.otf", FONT_SIZE)

        # ステータス表示領域の下にダンジョンを描画
        for x in range(self.width):
            for y in range(self.height):
                # 移動可能領域
                if self.dungeon_size[x][y] == 1:
                    pygame.draw.rect(self.screen, WHITE, (x * 10, y * 10 + DISP_SPACE, 10, 10))
                # 階段
                elif self.dungeon_size[x][y] == 2:
                    pygame.draw.rect(self.screen, YELLOW, (x * 10, y * 10 + DISP_SPACE, 10, 10))
                # 敵
                elif self.dungeon_size[x][y] == 3:
                    pygame.draw.rect(self.screen, GREEN, (x * 10, y * 10 + DISP_SPACE, 10, 10))
                # 移動不可領域
                else:
                    pygame.draw.rect(self.screen, BLACK, (x * 10, y * 10 + DISP_SPACE, 10, 10))

        # ステータス描画領域を黒で塗りつぶす
        for x in range(self.width):
            pygame.draw.rect(self.screen, BLACK, (x * 10, 0, 10, DISP_SPACE))
        # 現在の階層を表示
        text = self.font.render(f"現在{self.layer}階層", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        # 現在HPを表示
        text = self.font.render(f"HP:{self.player_data.HP}", True, (255, 255, 255))
        self.screen.blit(text, (10, 35))

    # プレイヤーの描画
    def draw_player(self):
        pygame.draw.rect(self.screen, RED, (self.player_pos[0] * 10, self.player_pos[1] * 10 + DISP_SPACE, 10, 10))

    # 敵の描画
    def draw_enemy(self):
        pygame.draw.rect(self.screen, BLUE, (self.enemy_pos[0] * 10, self.enemy_pos[1] * 10 + DISP_SPACE, 10, 10))

    # 敵の移動
    def enemy_move(self):
        ran = random.randint(1, 4)
        # 上へ移動
        if ran == 1:
            # 移動可能判定(移動先が黒マスなら移動しない)
            if self.dungeon_size[self.enemy_pos[0]][self.enemy_pos[1] - 1] != 0:
                self.enemy_pos[1] -= 1
        # 下へ移動
        elif ran == 2:
            # 移動可能判定(移動先が黒マスなら移動しない)
            if self.dungeon_size[self.enemy_pos[0]][self.enemy_pos[1] + 1] != 0:
                self.enemy_pos[1] += 1
        # 左へ移動
        elif ran == 3:
            # 移動可能判定(移動先が黒マスなら移動しない)
            if self.dungeon_size[self.enemy_pos[0] - 1][self.enemy_pos[1]] != 0:
                self.enemy_pos[0] -= 1
        # 右へ移動
        elif ran == 4:
            # 移動可能判定(移動先が黒マスなら移動しない)
            if self.dungeon_size[self.enemy_pos[0] + 1][self.enemy_pos[1]] != 0:
                self.enemy_pos[0] += 1

    # 敵との接触判定
    def check_collision(self):
        if self.player_pos[0] == self.enemy_pos[0] and self.player_pos[1] == self.enemy_pos[1]:
            return True
        else:
            return False

    # 敵との戦闘(HPに10ダメージを受けて敵を再配置)
    def battle_event(self):
        # ダメージの計算
        self.player_data.HP -= 10

        # 敵オブジェクトを再配置する
        selected_cell = random.choice(self.movable_area)
        self.enemy_pos = [selected_cell[1], selected_cell[0]]


# ステータスウィンドウを閉じる
def close_window(event):
    event.widget.destroy()


# ステータスウィンドウを開く
def show_menu():
    # ウィンドウの作成
    window = tk.Tk()
    window.title("ステータス")

    # ウィンドウのサイズを設定
    window.geometry("600x400")

    # ウィンドウにフォーカスを移す
    window.focus_set()

    # ボタンの作成
    # new_game_button = tk.Button(window, text="New Game", command=new_game)
    # load_game_button = tk.Button(window, text="Load Game", command=load_game)
    # options_button = tk.Button(window, text="Options", command=options)

    # ボタンの配置
    # new_game_button.pack()
    # load_game_button.pack()
    # options_button.pack()

    # 閉じるボタンの作成、配置
    quit_button = tk.Button(window, text="閉じる", command=window.quit)
    quit_button.pack()

    # zキーで閉じる
    window.bind('<z>', close_window)

    # イベントループを開始
    window.mainloop()


# データ保存
def save_data(player_data):
    # データベースに接続する
    conn = sqlite3.connect(PLAYER_DB)
    cursor = conn.cursor()

    # テーブルが存在しない場合は作成する
    cursor.execute('''CREATE TABLE IF NOT EXISTS players
                      (name TEXT, hp INTEGER, mp INTEGER)''')
    # データを挿入する
    cursor.execute('''INSERT INTO players VALUES (?, ?, ?)''',
                   (player_data.name, player_data.HP, player_data.MP))
    # 変更を保存する
    conn.commit()
    # データベースとの接続を閉じる
    conn.close()


def main():
    # Pygameの初期化
    pygame.init()
    pygame.font.init()

    # ダンジョン＆プレイヤーの生成
    dungeon = Dungeon(DUNGEON_WIDTH, DUNGEON_HEIGHT)
    dungeon.generate_dungeon()

    # Pygameのメインループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # sys.exit()

            # キー入力でプレイヤーを移動
            if event.type == pygame.KEYDOWN:
                # 上キー
                if event.key == pygame.K_UP:
                    # 移動可能判定(移動先が黒マスなら移動しない)
                    if dungeon.dungeon_size[dungeon.player_pos[0]][dungeon.player_pos[1] - 1] != 0:
                        dungeon.player_pos[1] -= 1
                        # 敵と接触した場合戦闘。接触しなかった場合は敵が移動する
                        if dungeon.check_collision():
                            dungeon.battle_event()
                        else:
                            dungeon.enemy_move()
                            if dungeon.check_collision():
                                dungeon.battle_event()
                # 下キー
                elif event.key == pygame.K_DOWN:
                    # 移動可能判定(移動先が黒マスなら移動しない)
                    if dungeon.dungeon_size[dungeon.player_pos[0]][dungeon.player_pos[1] + 1] != 0:
                        dungeon.player_pos[1] += 1
                        # 敵と接触した場合の処理
                        if dungeon.check_collision():
                            dungeon.battle_event()
                        else:
                            dungeon.enemy_move()
                            if dungeon.check_collision():
                                dungeon.battle_event()
                # 左キー
                elif event.key == pygame.K_LEFT:
                    # 移動可能判定(移動先が黒マスなら移動しない)
                    if dungeon.dungeon_size[dungeon.player_pos[0] - 1][dungeon.player_pos[1]] != 0:
                        dungeon.player_pos[0] -= 1
                        # 敵と接触した場合の処理
                        if dungeon.check_collision():
                            dungeon.battle_event()
                        else:
                            dungeon.enemy_move()
                            if dungeon.check_collision():
                                dungeon.battle_event()
                # 右キー
                elif event.key == pygame.K_RIGHT:
                    # 移動可能判定(移動先が黒マスなら移動しない)
                    if dungeon.dungeon_size[dungeon.player_pos[0] + 1][dungeon.player_pos[1]] != 0:
                        dungeon.player_pos[0] += 1
                        # 敵と接触した場合の処理
                        if dungeon.check_collision():
                            dungeon.battle_event()
                        else:
                            dungeon.enemy_move()
                            if dungeon.check_collision():
                                dungeon.battle_event()
                # zキー(ステータスウィンドウを開く)
                elif event.key == pygame.K_z:
                    show_menu()

        # 移動先のセルが青色(階段)の場合に新ダンジョンを生成する(下層に移動)
        if dungeon.dungeon_size[dungeon.player_pos[0]][dungeon.player_pos[1]] == 2:
            dungeon.layer += 1
            dungeon.generate_dungeon()

        # 回復の泉
        if dungeon.dungeon_size[dungeon.player_pos[0]][dungeon.player_pos[1]] == 3:
            dungeon.player_data.HP = dungeon.player_data.max_hp
            dungeon.dungeon_size[dungeon.player_pos[0]][dungeon.player_pos[1]] = 1

        # ダンジョンとプレイヤーの再描画
        dungeon.draw_dungeon()
        dungeon.draw_player()
        dungeon.draw_enemy()

        # 表示を更新
        pygame.display.update()


if __name__ == "__main__":
    main()
