import tkinter as tk
import random

# ══════════════════════════════════════════════════════════════════
#  THEME MANAGER
# ══════════════════════════════════════════════════════════════════

class ThemeManager:
    _THEMES = {
        'light': dict(bg='#FFFFFF', fg='#000000',
                      btn_bg='#000000', btn_fg='#FFFFFF',
                      canvas_bg='#FFFFFF'),
        'dark':  dict(bg='#111111', fg='#FFFFFF',
                      btn_bg='#FFFFFF', btn_fg='#000000',
                      canvas_bg='#111111'),
    }

    def __init__(self):
        self._mode = 'light'

    def get(self):
        return self._THEMES[self._mode]

    def toggle(self):
        self._mode = 'dark' if self._mode == 'light' else 'light'

    def is_dark(self):
        return self._mode == 'dark'


# ══════════════════════════════════════════════════════════════════
#  FALLING OBJECTS  (Base + Subclasses)
# ══════════════════════════════════════════════════════════════════

class FallingObject:
    """Abstract base for all items that fall from the sky."""
    name        = '?'
    score_value = 0
    is_good     = True
    width       = 30
    height      = 30

    def __init__(self, canvas, x, y, theme):
        self.canvas = canvas
        self.x      = x
        self.y      = y
        self.theme  = theme
        self._ids   = []
        self._draw()

    # ── override in subclasses ────────────────
    def _draw(self):
        pass

    # ── helpers ───────────────────────────────
    def _reg(self, *ids):
        """Register canvas item IDs for later deletion/movement."""
        self._ids.extend(ids)

    def move(self, dy):
        self.y += dy
        for cid in self._ids:
            self.canvas.move(cid, 0, dy)

    def delete(self):
        for cid in self._ids:
            self.canvas.delete(cid)
        self._ids.clear()

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def center_x(self):
        return self.x


# ──────────────────────────────────────────────────────────────────
class Pencil(FallingObject):
    """Pensil · +10 poin"""
    name        = 'Pensil'
    score_value = 10
    is_good     = True
    width       = 10
    height      = 44

    def _draw(self):
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        cx, y = self.x, self.y
        self._reg(
            # eraser cap (top)
            cv.create_rectangle(cx-5, y,    cx+5, y+8,  fill=bg, outline=fg, width=2),
            # body
            cv.create_rectangle(cx-5, y+8,  cx+5, y+36, fill=fg, outline=fg),
            # pointed tip
            cv.create_polygon( cx-5, y+36, cx+5, y+36, cx, y+46, fill=fg, outline=fg),
            # center groove on body
            cv.create_line(cx, y+10, cx, y+34, fill=bg, width=1),
            # score label
            cv.create_text(cx, y+22, text="+10", font=("Courier", 6, "bold"), fill=bg),
        )


# ──────────────────────────────────────────────────────────────────
class Book(FallingObject):
    """Buku · +20 poin"""
    name        = 'Buku'
    score_value = 20
    is_good     = True
    width       = 36
    height      = 30

    def _draw(self):
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        cx, y = self.x, self.y
        self._reg(
            cv.create_rectangle(cx-19, y, cx+19, y+32, fill=fg, outline=fg),   # body
            cv.create_rectangle(cx-19, y, cx-11, y+32, fill=bg, outline=fg),   # spine
            *[cv.create_line(cx-9, y+i*8+5, cx+17, y+i*8+5,                   # page lines
                             fill=bg, width=1) for i in range(3)],
            cv.create_text(cx+2, y+26, text="+20", font=("Courier", 6, "bold"), fill=bg),
        )


# ──────────────────────────────────────────────────────────────────
class Eraser(FallingObject):
    """Penghapus · +15 poin"""
    name        = 'Penghapus'
    score_value = 15
    is_good     = True
    width       = 34
    height      = 20

    def _draw(self):
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        cx, y = self.x, self.y
        self._reg(
            cv.create_rectangle(cx-17, y, cx+17, y+20, fill=fg, outline=fg),   # outer
            cv.create_rectangle(cx-17, y, cx+1,  y+20, fill=bg, outline=fg),   # label strip
            cv.create_text(cx+9, y+10, text="+15", font=("Courier", 6, "bold"), fill=bg),
        )


# ──────────────────────────────────────────────────────────────────
class Ruler(FallingObject):
    """Penggaris · +25 poin"""
    name        = 'Penggaris'
    score_value = 25
    is_good     = True
    width       = 56
    height      = 14

    def _draw(self):
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        cx, y = self.x, self.y
        self._reg(
            cv.create_rectangle(cx-28, y, cx+28, y+14, fill=fg, outline=fg),   # body
            cv.create_line(cx-28, y+7, cx+28, y+7, fill=bg, width=1),          # center line
            *[cv.create_line(cx-23+i*10, y, cx-23+i*10, y+7,                  # tick marks
                             fill=bg, width=1) for i in range(6)],
            cv.create_text(cx, y+11, text="+25", font=("Courier", 6, "bold"), fill=bg),
        )


# ──────────────────────────────────────────────────────────────────
class Trash(FallingObject):
    """Sampah · -20 poin & -1 nyawa"""
    name        = 'Sampah'
    score_value = -20
    is_good     = False
    width       = 30
    height      = 38

    def _draw(self):
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        cx, y = self.x, self.y
        self._reg(
            # bag tie
            cv.create_polygon(cx-3, y, cx+3, y, cx+7, y+9, cx-7, y+9,
                              fill=fg, outline=fg),
            # bag body
            cv.create_oval(cx-15, y+7, cx+15, y+38, fill=fg, outline=fg),
            # X marks
            cv.create_line(cx-8, y+16, cx+8, y+30, fill=bg, width=2),
            cv.create_line(cx+8, y+16, cx-8, y+30, fill=bg, width=2),
            cv.create_text(cx, y+34, text="-20", font=("Courier", 6, "bold"), fill=bg),
        )


# ══════════════════════════════════════════════════════════════════
#  BASKET
# ══════════════════════════════════════════════════════════════════

class Basket:
    WIDTH  = 78
    HEIGHT = 34
    SPEED  = 22
    TAG    = 'basket'

    def __init__(self, canvas, x, y, theme, canvas_w):
        self.canvas = canvas
        self.x      = x
        self.y      = y
        self.theme  = theme
        self._cw    = canvas_w
        self._draw()

    def _draw(self):
        """Draw basket from scratch using canvas TAG for bulk movement."""
        self.canvas.delete(self.TAG)
        fg, bg, cv = self.theme['fg'], self.theme['canvas_bg'], self.canvas
        x, y, hw, h = self.x, self.y, self.WIDTH // 2, self.HEIGHT
        # Trapezoid (wider at top = opening)
        cv.create_polygon(x-hw, y, x+hw, y, x+hw-8, y+h, x-hw+8, y+h,
                          fill=bg, outline=fg, width=2, tags=self.TAG)
        # Horizontal weave lines
        for i in range(1, 3):
            cv.create_line(x-hw+i*3, y+i*12, x+hw-i*3, y+i*12,
                           fill=fg, width=1, tags=self.TAG)
        # Vertical weave lines
        for i in range(-3, 4):
            cv.create_line(x+i*11, y, x+i*9, y+h,
                           fill=fg, width=1, tags=self.TAG)

    def move_left(self):
        hw = self.WIDTH // 2
        new_x = max(hw + 3, self.x - self.SPEED)
        if new_x != self.x:
            self.canvas.move(self.TAG, new_x - self.x, 0)
            self.x = new_x

    def move_right(self):
        hw = self.WIDTH // 2
        new_x = min(self._cw - hw - 3, self.x + self.SPEED)
        if new_x != self.x:
            self.canvas.move(self.TAG, new_x - self.x, 0)
            self.x = new_x

    def get_rect(self):
        hw = self.WIDTH // 2
        return self.x - hw, self.y, self.x + hw, self.y + self.HEIGHT

    def refresh(self, theme):
        self.theme = theme
        self._draw()


# ══════════════════════════════════════════════════════════════════
#  SCORE POPUP  (floating +/- text)
# ══════════════════════════════════════════════════════════════════

class ScorePopup:
    LIFE = 28  # frames before disappearing

    def __init__(self, canvas, x, y, text, theme):
        self.canvas = canvas
        self._id    = canvas.create_text(
            x, y, text=text,
            font=("Courier", 14, "bold"),
            fill=theme['fg']
        )
        self._life  = self.LIFE

    def tick(self):
        self.canvas.move(self._id, 0, -2)
        self._life -= 1

    @property
    def dead(self):
        return self._life <= 0

    def delete(self):
        self.canvas.delete(self._id)


# ══════════════════════════════════════════════════════════════════
#  SCORE MANAGER
# ══════════════════════════════════════════════════════════════════

class ScoreManager:
    TARGET = 450

    def __init__(self, difficulty):
        self.score = 0
        self.lives = 5 if difficulty == 'easy' else 3

    def add(self, value):
        self.score = max(0, self.score + value)

    def lose_life(self):
        self.lives -= 1

    @property
    def game_over(self):
        return self.lives <= 0

    @property
    def win(self):
        return self.score >= self.TARGET


# ══════════════════════════════════════════════════════════════════
#  BASE SCREEN
# ══════════════════════════════════════════════════════════════════

class BaseScreen:
    def __init__(self, app):
        self.app   = app
        self.root  = app.root
        self.tm    = app.theme_manager
        self.frame = None

    def show(self):
        t = self.tm.get()
        self.frame = tk.Frame(self.root, bg=t['bg'])
        self.frame.pack(fill='both', expand=True)
        self.build()

    def hide(self):
        if self.frame:
            self.frame.destroy()
            self.frame = None

    def build(self):
        pass

    # ── Widget helpers ────────────────────────
    def _btn(self, parent, text, cmd, *, w=14, h=2, inv=False):
        t = self.tm.get()
        bg = t['bg'] if inv else t['btn_bg']
        fg = t['fg'] if inv else t['btn_fg']
        return tk.Button(
            parent, text=text, command=cmd,
            font=("Courier", 12, "bold"),
            bg=bg, fg=fg,
            activebackground=fg, activeforeground=bg,
            relief='flat', cursor='hand2',
            width=w, height=h,
            highlightthickness=2,
            highlightbackground=t['fg'],
        )

    def _lbl(self, parent, text, sz=13, bold=False, **kw):
        t = self.tm.get()
        return tk.Label(
            parent, text=text,
            font=("Courier", sz, "bold" if bold else "normal"),
            bg=kw.get('bg', t['bg']),
            fg=kw.get('fg', t['fg']),
        )

    def _div(self, parent, w=300, h=2):
        return tk.Frame(parent, bg=self.tm.get()['fg'], width=w, height=h)


# ══════════════════════════════════════════════════════════════════
#  MAIN MENU SCREEN
# ══════════════════════════════════════════════════════════════════

class MainMenuScreen(BaseScreen):
    def build(self):
        t = self.tm.get()
        self.frame.configure(bg=t['bg'])

        wrap = tk.Frame(self.frame, bg=t['bg'])
        wrap.place(relx=0.5, rely=0.48, anchor='center')

        # Title
        self._lbl(wrap, "CATCH\nTHE\nOBJECTS", sz=30, bold=True).pack()
        self._div(wrap, w=300, h=3).pack(pady=16)

        # Menu buttons
        for txt, cmd in [
            ("▶   PLAY",    self.app.show_difficulty),
            ("⚙   SETTING", self.app.show_settings),
            ("✕   EXIT",    self.root.quit),
        ]:
            self._btn(wrap, txt, cmd).pack(pady=7)

        # Footer
        self._lbl(self.frame, "Pixel Edition  •  v1.0", sz=8)\
            .place(relx=0.5, rely=0.97, anchor='s')


# ══════════════════════════════════════════════════════════════════
#  DIFFICULTY SCREEN
# ══════════════════════════════════════════════════════════════════

class DifficultyScreen(BaseScreen):
    def build(self):
        t = self.tm.get()
        self.frame.configure(bg=t['bg'])

        wrap = tk.Frame(self.frame, bg=t['bg'])
        wrap.place(relx=0.5, rely=0.5, anchor='center')

        self._lbl(wrap, "PILIH KESULITAN", sz=20, bold=True).pack()
        self._div(wrap, w=300).pack(pady=10)

        # Difficulty cards
        for label, diff, info in [
            ("★   EASY", 'easy', "5 Nyawa  •  Kecepatan Lambat"),
            ("★★  HARD", 'hard', "3 Nyawa  •  Kecepatan Cepat"),
        ]:
            card = tk.Frame(wrap, bg=t['bg'])
            card.pack(pady=12)
            self._btn(card, label,
                      lambda d=diff: self.app.start_game(d),
                      w=16).pack()
            self._lbl(card, info, sz=9).pack(pady=3)

        self._div(wrap, w=300, h=1).pack(pady=12)
        self._btn(wrap, "← KEMBALI", self.app.show_main_menu,
                  inv=True, w=10, h=1).pack()


# ══════════════════════════════════════════════════════════════════
#  SETTINGS SCREEN
# ══════════════════════════════════════════════════════════════════

class SettingsScreen(BaseScreen):
    def build(self):
        t = self.tm.get()
        self.frame.configure(bg=t['bg'])

        wrap = tk.Frame(self.frame, bg=t['bg'])
        wrap.place(relx=0.5, rely=0.5, anchor='center')

        self._lbl(wrap, "PENGATURAN", sz=20, bold=True).pack()
        self._div(wrap, w=220).pack(pady=10)

        # Theme section
        self._lbl(wrap, "TEMA", sz=14, bold=True).pack(pady=(20, 5))
        mode = "GELAP (Dark)" if self.tm.is_dark() else "TERANG (Light)"
        self._lbl(wrap, f"Saat ini : {mode}", sz=10).pack()

        nxt = "→ Ganti ke LIGHT" if self.tm.is_dark() else "→ Ganti ke DARK"
        self._btn(wrap, nxt, self.app.toggle_theme, w=18).pack(pady=10)

        self._div(wrap, w=220, h=1).pack(pady=16)
        self._btn(wrap, "← KEMBALI", self.app.show_main_menu,
                  inv=True, w=10, h=1).pack()


# ══════════════════════════════════════════════════════════════════
#  GAME SCREEN
# ══════════════════════════════════════════════════════════════════

class GameScreen(BaseScreen):
    CW = 500   # canvas width
    CH = 560   # canvas height

    # Object pool: classes & spawn weights
    _CLASSES = [Pencil, Book, Eraser, Ruler, Trash]
    _WEIGHTS = [22, 17, 20, 16, 10]

    def __init__(self, app, difficulty):
        super().__init__(app)
        self.difficulty = difficulty
        self._speed     = 1.8 if difficulty == 'easy' else 3.6
        self._spawn_ms  = 1900 if difficulty == 'easy' else 1100
        self.sm         = ScoreManager(difficulty)
        self.basket     = None
        self.objects    = []   # active FallingObject instances
        self.popups     = []   # active ScorePopup instances
        self.keys       = set()
        self.paused     = False
        self.running    = False
        self._afters    = []   # after() IDs to cancel on exit

    # ── Build UI ──────────────────────────────────────────────────
    def build(self):
        t = self.tm.get()
        self.frame.configure(bg=t['bg'])

        # ── Top bar ──────────────────────────────────
        bar = tk.Frame(self.frame, bg=t['bg'])
        bar.pack(fill='x', padx=10, pady=(8, 4))

        self.score_lbl = tk.Label(
            bar, text=self._score_txt(),
            font=("Courier", 12, "bold"),
            bg=t['bg'], fg=t['fg']
        )
        self.score_lbl.pack(side='left')

        self.lives_lbl = tk.Label(
            bar, text=self._lives_txt(),
            font=("Courier", 12, "bold"),
            bg=t['bg'], fg=t['fg']
        )
        self.lives_lbl.pack(side='left', padx=14)

        tk.Label(
            bar, text=f"[{self.difficulty.upper()}]",
            font=("Courier", 10, "bold"),
            bg=t['bg'], fg=t['fg']
        ).pack(side='left')

        self.pause_btn = tk.Button(
            bar, text="⏸ PAUSE",
            font=("Courier", 10, "bold"),
            bg=t['btn_bg'], fg=t['btn_fg'],
            relief='flat', cursor='hand2',
            command=self.toggle_pause
        )
        self.pause_btn.pack(side='right')

        # ── Canvas ───────────────────────────────────
        self.cv = tk.Canvas(
            self.frame,
            width=self.CW, height=self.CH,
            bg=t['canvas_bg'],
            highlightthickness=2,
            highlightbackground=t['fg']
        )
        self.cv.pack()

        # ── Hint ─────────────────────────────────────
        tk.Label(
            self.frame,
            text="← → / A D  Gerakkan Keranjang   |   P  Pause",
            font=("Courier", 8),
            bg=t['bg'], fg=t['fg']
        ).pack(pady=4)

        self._init_game()

    # ── Init game ─────────────────────────────────────────────────
    def _init_game(self):
        t = self.tm.get()
        self.basket = Basket(self.cv, self.CW // 2, self.CH - 65, t, self.CW)
        self.running = True
        self._bind_keys()
        self._schedule_spawn()
        self._loop()

    # ── Key bindings ──────────────────────────────────────────────
    def _bind_keys(self):
        b = self.root.bind
        b('<Left>',             lambda e: self.keys.add('l'))
        b('<Right>',            lambda e: self.keys.add('r'))
        b('<a>',                lambda e: self.keys.add('l'))
        b('<d>',                lambda e: self.keys.add('r'))
        b('<KeyRelease-Left>',  lambda e: self.keys.discard('l'))
        b('<KeyRelease-Right>', lambda e: self.keys.discard('r'))
        b('<KeyRelease-a>',     lambda e: self.keys.discard('l'))
        b('<KeyRelease-d>',     lambda e: self.keys.discard('r'))
        b('<p>',                lambda e: self.toggle_pause())
        b('<P>',                lambda e: self.toggle_pause())

    def _unbind_keys(self):
        for k in ('<Left>', '<Right>', '<a>', '<d>',
                  '<KeyRelease-Left>', '<KeyRelease-Right>',
                  '<KeyRelease-a>', '<KeyRelease-d>', '<p>', '<P>'):
            try:
                self.root.unbind(k)
            except Exception:
                pass

    def _cancel_afters(self):
        for a in self._afters:
            try:
                self.root.after_cancel(a)
            except Exception:
                pass
        self._afters.clear()

    def hide(self):
        self.running = False
        self._unbind_keys()
        self._cancel_afters()
        super().hide()

    # ── HUD helpers ───────────────────────────────────────────────
    def _score_txt(self):
        return f"SKOR: {self.sm.score}/{ScoreManager.TARGET}"

    def _lives_txt(self):
        return "♥ " * self.sm.lives

    def _update_hud(self):
        self.score_lbl.config(text=self._score_txt())
        self.lives_lbl.config(text=self._lives_txt())

    # ── Spawn logic ───────────────────────────────────────────────
    def _schedule_spawn(self):
        if not self.running:
            return
        aid = self.root.after(self._spawn_ms, self._spawn)
        self._afters.append(aid)

    def _spawn(self):
        if not self.running:
            return
        if not self.paused:
            t = self.tm.get()
            x   = random.randint(55, self.CW - 55)
            cls = random.choices(self._CLASSES, weights=self._WEIGHTS)[0]
            self.objects.append(cls(self.cv, x, -65, t))
        self._schedule_spawn()

    # ── Main game loop (~60 fps) ──────────────────────────────────
    def _loop(self):
        if not self.running:
            return

        if not self.paused:
            # Basket movement
            if 'l' in self.keys:
                self.basket.move_left()
            if 'r' in self.keys:
                self.basket.move_right()

            # Objects movement + collision
            self._process_objects()

            # Animate score popups
            for p in self.popups[:]:
                p.tick()
                if p.dead:
                    p.delete()
                    self.popups.remove(p)

            # Refresh HUD
            self._update_hud()

            # End conditions
            if self.sm.game_over:
                self._show_end(won=False)
                return
            if self.sm.win:
                self._show_end(won=True)
                return

        aid = self.root.after(16, self._loop)
        self._afters.append(aid)

    def _process_objects(self):
        bx1, by1, bx2, _ = self.basket.get_rect()
        threshold = by1 + self._speed + 18  # collision window

        for obj in self.objects[:]:
            obj.move(self._speed)

            # Fell off bottom → remove silently
            if obj.y > self.CH + 20:
                obj.delete()
                self.objects.remove(obj)
                continue

            # Collision: object bottom enters basket opening
            if (by1 <= obj.bottom <= threshold and
                    bx1 <= obj.center_x <= bx2):
                self._catch(obj)
                obj.delete()
                self.objects.remove(obj)

    def _catch(self, obj):
        """Handle an object landing in the basket."""
        self.sm.add(obj.score_value)

        # Popup text
        sign = '+' if obj.score_value >= 0 else ''
        popup_text = f"{sign}{obj.score_value}"

        if not obj.is_good:
            self.sm.lose_life()
            popup_text += " -♥"   # visual life-loss indicator

        self.popups.append(
            ScorePopup(self.cv, obj.center_x, self.basket.y - 20,
                       popup_text, self.tm.get())
        )

    # ── Pause / Resume ────────────────────────────────────────────
    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        t = self.tm.get()

        if self.paused:
            self.pause_btn.config(text="▶ RESUME")
            cx, cy = self.CW // 2, self.CH // 2
            self._pause_box = self.cv.create_rectangle(
                cx-148, cy-78, cx+148, cy+78,
                fill=t['canvas_bg'], outline=t['fg'], width=3
            )
            self._pause_txt = self.cv.create_text(
                cx, cy,
                text="⏸  JEDA\n\n[P] untuk melanjutkan",
                font=("Courier", 18, "bold"),
                fill=t['fg'], justify='center'
            )
        else:
            self.pause_btn.config(text="⏸ PAUSE")
            for attr in ('_pause_box', '_pause_txt'):
                if hasattr(self, attr):
                    self.cv.delete(getattr(self, attr))

    # ── End game overlay ──────────────────────────────────────────
    def _show_end(self, won):
        self.running = False
        self._unbind_keys()
        self._cancel_afters()

        t = self.tm.get()
        cx, cy = self.CW // 2, self.CH // 2

        # Panel background
        self.cv.create_rectangle(
            cx-215, cy-175, cx+215, cy+175,
            fill=t['canvas_bg'], outline=t['fg'], width=3
        )

        # Header
        title = "★  KAMU MENANG!  ★" if won else "✕  GAME OVER  ✕"
        self.cv.create_text(
            cx, cy - 125,
            text=title,
            font=("Courier", 18, "bold"),
            fill=t['fg']
        )

        # Stats
        self.cv.create_text(
            cx, cy - 82,
            text=f"Skor Akhir : {self.sm.score}/{ScoreManager.TARGET}",
            font=("Courier", 13),
            fill=t['fg']
        )
        self.cv.create_text(
            cx, cy - 54,
            text=f"Difficulty : {self.difficulty.upper()}",
            font=("Courier", 12),
            fill=t['fg']
        )

        # Divider
        self.cv.create_line(cx-165, cy-28, cx+165, cy-28,
                            fill=t['fg'], width=1)

        # Scoreboard reminder
        self.cv.create_text(
            cx, cy - 8,
            text="Pensil+10  Hapus+15  Buku+20  Garis+25",
            font=("Courier", 8),
            fill=t['fg']
        )

        # Action buttons (embedded in canvas via create_window)
        for lbl, cmd, oy in [
            ("↺  MAIN LAGI",
             lambda: self.root.after(0, lambda: self.app.start_game(self.difficulty)),
             45),
            ("⌂  MENU UTAMA",
             lambda: self.root.after(0, self.app.show_main_menu),
             100),
        ]:
            btn = tk.Button(
                self.cv, text=lbl,
                font=("Courier", 11, "bold"),
                bg=t['btn_bg'], fg=t['btn_fg'],
                relief='flat', cursor='hand2',
                command=cmd
            )
            self.cv.create_window(cx, cy + oy,
                                  window=btn, width=195, height=40)


# ══════════════════════════════════════════════════════════════════
#  APPLICATION  (root controller)
# ══════════════════════════════════════════════════════════════════

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Catch Falling Objects")
        self.root.geometry("520x720")
        self.root.resizable(False, False)

        self.theme_manager = ThemeManager()
        self._screen: BaseScreen | None = None

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_main_menu()
        self.root.mainloop()

    # ── Screen switching ──────────────────────────────────────────
    def _switch(self, screen: BaseScreen):
        if self._screen:
            self._screen.hide()
        self._screen = screen
        self._screen.show()
        self.root.configure(bg=self.theme_manager.get()['bg'])

    # ── Public navigation methods ─────────────────────────────────
    def show_main_menu(self):
        self._switch(MainMenuScreen(self))

    def show_difficulty(self):
        self._switch(DifficultyScreen(self))

    def show_settings(self):
        self._switch(SettingsScreen(self))

    def toggle_theme(self):
        self.theme_manager.toggle()
        self.show_settings()

    def start_game(self, difficulty: str):
        self._switch(GameScreen(self, difficulty))

    # ── Safe close ────────────────────────────────────────────────
    def _on_close(self):
        if self._screen and hasattr(self._screen, 'running'):
            self._screen.running = False
        self.root.destroy()


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    App()
