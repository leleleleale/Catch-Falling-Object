import tkinter as tk
import random
import time

# ======================== CLASS OBJECT ========================
class GameObject:
    def __init__(self, canvas, x, y, speed, skor, jenis):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.speed = speed
        self.skor = skor
        self.jenis = jenis     
        self.id = None
        self.width = 30
        self.height = 30
        self.active = True

    def draw(self):
        color = "white"
        if self.jenis == 'pensil':
            self.id = self.canvas.create_rectangle(
                self.x, self.y, self.x+6, self.y+25, fill=color, outline=color)
        elif self.jenis == 'buku':
            self.id = self.canvas.create_rectangle(
                self.x, self.y, self.x+28, self.y+22, fill=color, outline=color)
            self.canvas.create_line(
                self.x+14, self.y, self.x+14, self.y+22, fill="black")
        elif self.jenis == 'penghapus':
            self.id = self.canvas.create_rectangle(
                self.x, self.y, self.x+18, self.y+20, fill=color, outline=color)
        elif self.jenis == 'penggaris':
            self.id = self.canvas.create_rectangle(
                self.x, self.y, self.x+8, self.y+30, fill=color, outline=color)
        elif self.jenis == 'sampah':
            self.id = self.canvas.create_polygon(
                self.x, self.y+15, self.x+10, self.y,
                self.x+22, self.y+10, self.x+18, self.y+25,
                self.x+5, self.y+22, fill=color, outline=color)

    def fall(self):
        if self.active:
            self.canvas.move(self.id, 0, self.speed)
            self.y += self.speed
            if self.y > 720:
                self.active = False
                self.canvas.delete(self.id)
                return False
        return True

    def get_coords(self):
        if self.active and self.id:
            return self.canvas.bbox(self.id)
        return None


# ======================== CLASS BASKET ========================
class Basket:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 80
        self.height = 30
        self.x = 600
        self.y = 650
        self.speed = 30
        self.id = self.canvas.create_rectangle(
            self.x, self.y, self.x+self.width, self.y+self.height,
            fill="white", outline="white")

    def move_left(self, event=None):
        if self.x > 0:
            self.x -= self.speed
            self.canvas.move(self.id, -self.speed, 0)

    def move_right(self, event=None):
        if self.x < 990:
            self.x += self.speed
            self.canvas.move(self.id, self.speed, 0)

    def get_coords(self):
        return self.canvas.coords(self.id)


# ======================== CLASS SCORE POPUP ========================
class ScorePopup:
    def __init__(self, canvas, x, y, text, color="white"):
        self.canvas = canvas
        self.id = self.canvas.create_text(
            x, y, text=text, fill=color, font=("Courier", 16, "bold"))
        self.start_time = time.time()
        self.duration = 0.8

    def update(self):
        if time.time() - self.start_time > self.duration:
            self.canvas.delete(self.id)
            return False
        return True


# ======================== CLASS GAME ========================
class Game:
    def __init__(self, root, difficulty='easy', tema='dark'):
        self.root = root
        self.difficulty = difficulty
        self.tema = tema
        self.canvas = tk.Canvas(root, width=1280, height=720, highlightthickness=0)
        self.canvas.pack()

        if tema == 'dark':
            self.bg = 'black'
            self.fg = 'white'
        else:
            self.bg = 'white'
            self.fg = 'black'
        self.canvas.configure(bg=self.bg)

        self.target_skor = 300
        self.skor = 0
        self.nyawa = 5 if difficulty == 'easy' else 3
        self.game_over = False
        self.paused = False
        self.loop_running = False 

        if difficulty == 'easy':
            self.base_speed = 3
            self.spawn_rate = 55  
            self.sampah_chance = 0.25
        else:
            self.base_speed = 8
            self.spawn_rate = 30
            self.sampah_chance = 0.5


        self.basket = Basket(self.canvas)
        self.objects = []
        self.popups = []
        self.frame_count = 0
        self.ui_skor = self.canvas.create_text(
            100, 30, text=f"0/{self.target_skor}", fill=self.fg, font=("Courier", 18, "bold"))
        self.ui_nyawa = self.canvas.create_text(
            200, 30, text=f"♥ {self.nyawa}", fill=self.fg, font=("Courier", 18, "bold"))
        self.pause_btn = self.canvas.create_text(
            1230, 30, text="⏸ Pause", fill=self.fg, font=("Courier", 14, "bold"),
            activefill="gray")
        self.canvas.tag_bind(self.pause_btn, "<Button-1>", lambda e: self.toggle_pause())

        root.bind("<Left>", self.basket.move_left)
        root.bind("<Right>", self.basket.move_right)
        root.bind("<a>", self.basket.move_left)
        root.bind("<A>", self.basket.move_left)
        root.bind("<d>", self.basket.move_right)
        root.bind("<D>", self.basket.move_right)
        root.bind("<p>", lambda e: self.toggle_pause())
        root.bind("<P>", lambda e: self.toggle_pause())

        self.game_loop()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.canvas.itemconfig(self.pause_btn, text="▶ Play")
            self.loop_running = False
        else:
            self.canvas.itemconfig(self.pause_btn, text="⏸ Pause")
            if not self.loop_running:
                self.game_loop()

    def spawn_object(self):
        if random.random() < self.sampah_chance:
            jenis = 'sampah'
            skor = -30 if self.difficulty == 'easy' else -50
        else:
            barang = [
                ('pensil', 10),
                ('buku', 20),
                ('penghapus', 15),
                ('penggaris', 25)
            ]
            jenis, skor = random.choice(barang)

        x = random.randint(50, 1000)
        obj = GameObject(self.canvas, x, 0, self.base_speed, skor, jenis)
        obj.draw()
        self.objects.append(obj)

    def check_collision(self, obj):
        if not obj.active:
            return False
        basket_coords = self.basket.get_coords()
        obj_coords = obj.get_coords()
        if not basket_coords or not obj_coords:
            return False
        bx1, by1, bx2, by2 = basket_coords
        ox1, oy1, ox2, oy2 = obj_coords
        if (bx1 < ox2 and bx2 > ox1 and by1 < oy2 and by2 > oy1):
            return True
        return False

    def handle_catch(self, obj):
        self.skor += obj.skor
        if self.skor < 0:
            self.skor = 0  
        if obj.skor > 0:
            text = f"+{int(obj.skor)}"
        else:
            text = f"{int(obj.skor)}"
        popup = ScorePopup(self.canvas, self.basket.x+40, self.basket.y-20, text, self.fg)
        self.popups.append(popup)

        if obj.jenis == 'sampah':
            self.nyawa -= 1
            self.canvas.itemconfig(self.ui_nyawa, text=f"♥ {self.nyawa}")

        obj.active = False
        self.canvas.delete(obj.id)
        self.objects.remove(obj)
        self.canvas.itemconfig(self.ui_skor, text=f"{self.skor}/{self.target_skor}")

        if self.skor >= self.target_skor:
            self.end_game("menang")
        elif self.nyawa <= 0:
            self.end_game("kalah")

    def end_game(self, hasil):
        self.game_over = True
        self.loop_running = False
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")
        self.root.unbind("<a>")
        self.root.unbind("<A>")
        self.root.unbind("<d>")
        self.root.unbind("<D>")
        self.canvas.create_text(
            640, 360, text=f"GAME {hasil.upper()}", fill=self.fg,
            font=("Courier", 36, "bold"))
        self.root.after(1500, self.back_to_menu)

    def back_to_menu(self):
        self.canvas.destroy()
        Menu(self.root, self.tema)

    def game_loop(self):
        if self.game_over or self.paused:
            self.loop_running = False
            return
        self.loop_running = True
        self.frame_count += 1
        if self.frame_count % self.spawn_rate == 0:
            self.spawn_object()

        for obj in self.objects[:]:
            if not obj.fall():  
                if obj in self.objects:
                    self.objects.remove(obj)
            elif self.check_collision(obj):
                self.handle_catch(obj)
                if self.game_over:
                    return
                  
        for pop in self.popups[:]:
            if not pop.update():
                self.popups.remove(pop)

        if not self.game_over and not self.paused:
            self.root.after(30, self.game_loop)
        else:
            self.loop_running = False


# ======================== CLASS MENU ========================
class Menu:
    def __init__(self, root, tema='dark'):
        self.root = root
        self.tema = tema
        self.canvas = tk.Canvas(root, width=1080, height=720, highlightthickness=0)
        self.canvas.pack()

        if tema == 'dark':
            self.bg = 'black'
            self.fg = 'white'
        else:
            self.bg = 'white'
            self.fg = 'black'
        self.canvas.configure(bg=self.bg)

        self.canvas.create_text(
            540, 150, text="CATCH FALLING OBJECT",
            fill=self.fg, font=("Courier", 32, "bold"))
        self.canvas.create_text(
            540, 200, text="[ PIXEL EDITION ]",
            fill=self.fg, font=("Courier", 16))

        self.play_btn = self.canvas.create_text(
            540, 320, text="▶ PLAY", fill=self.fg,
            font=("Courier", 24, "bold"), activefill="gray")
        self.canvas.tag_bind(self.play_btn, "<Button-1>", self.choose_difficulty)

        self.settings_btn = self.canvas.create_text(
            540, 400, text="⚙ SETTINGS", fill=self.fg,
            font=("Courier", 24, "bold"), activefill="gray")
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", self.open_settings)

        self.exit_btn = self.canvas.create_text(
            540, 480, text="✕ EXIT", fill=self.fg,
            font=("Courier", 24, "bold"), activefill="gray")
        self.canvas.tag_bind(self.exit_btn, "<Button-1>", lambda e: root.destroy())

    def choose_difficulty(self, event):
        self.canvas.delete("all")
        self.canvas.create_text(
            540, 200, text="SELECT DIFFICULTY",
            fill=self.fg, font=("Courier", 28, "bold"))

        easy_btn = self.canvas.create_text(
            540, 320, text="EASY (♥ 5)", fill=self.fg,
            font=("Courier", 22), activefill="gray")
        hard_btn = self.canvas.create_text(
            540, 400, text="HARD (♥ 3)", fill=self.fg,
            font=("Courier", 22), activefill="gray")
        back_btn = self.canvas.create_text(
            540, 560, text="← BACK", fill=self.fg,
            font=("Courier", 18), activefill="gray")

        self.canvas.tag_bind(easy_btn, "<Button-1>",
                              lambda e: self.start_game('easy'))
        self.canvas.tag_bind(hard_btn, "<Button-1>",
                              lambda e: self.start_game('hard'))
        self.canvas.tag_bind(back_btn, "<Button-1>",
                              lambda e: self.refresh_menu())

    def start_game(self, difficulty):
        self.canvas.destroy()
        Game(self.root, difficulty, self.tema)

    def open_settings(self, event):
        self.canvas.delete("all")
        self.canvas.create_text(
            540, 200, text="SETTINGS",
            fill=self.fg, font=("Courier", 28, "bold"))
        self.canvas.create_text(
            540, 280, text=f"Current theme: {'DARK' if self.tema=='dark' else 'LIGHT'}",
            fill=self.fg, font=("Courier", 18))

        toggle_btn = self.canvas.create_text(
            540, 360, text="TOGGLE THEME", fill=self.fg,
            font=("Courier", 22, "bold"), activefill="gray")
        back_btn = self.canvas.create_text(
            540, 440, text="← BACK", fill=self.fg,
            font=("Courier", 18), activefill="gray")

        self.canvas.tag_bind(toggle_btn, "<Button-1>", self.toggle_theme)
        self.canvas.tag_bind(back_btn, "<Button-1>", lambda e: self.refresh_menu())

    def toggle_theme(self, event):
        self.tema = 'light' if self.tema == 'dark' else 'dark'
        self.open_settings(None) 

    def refresh_menu(self):
        self.canvas.destroy()
        Menu(self.root, self.tema)


# ======================== MAIN ========================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Catch Falling Object - Pixel Edition")
    root.geometry("1080x720")
    root.resizable(False, False)
    Menu(root, tema='dark')
    root.mainloop()
