import time
import tkinter as tk
import sys, os
import numpy as np
import random
from PIL import ImageTk, Image
import userpaths
import math
from pydub import AudioSegment
from pydub.playback import play


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_db():
    global PHRASES
    if os.path.exists(os.path.join(SAVE_PATH, 'PHRASES.npy')):
        PHRASES = np.load(os.path.join(SAVE_PATH, 'PHRASES.npy'))
    PHRASES = np.char.upper(PHRASES)


def save_db():
    global PHRASES
    if not os.path.isdir(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    PHRASES = np.char.upper(PHRASES)
    np.save(os.path.join(SAVE_PATH, 'PHRASES.npy'), PHRASES)


class GameWindow():
    def __init__(self, master, phrase, show_phrase, hide_phrase):
        self.displayed = False
        self.phrase = phrase
        self.guessed_characters = []
        self.phrase_characters = list(set([*self.phrase]))
        if ' ' in self.phrase_characters:
            self.phrase_characters.remove(' ')
        self.master = master
        self.window = None
        self.show_phrase = show_phrase
        self.hide_phrase = hide_phrase
        self.has_celebrated = False

    def display(self):
        self.window = tk.Toplevel(self.master)
        self.window.bind("<KeyRelease>", self.keyup)
        self.window.bind("<KeyPress>", self.keydown)
        self.window.title("Raa Lykkehjulet")
        self.window.geometry("1920x1015")
        self.window.state('zoomed')
        self.canvas = tk.Canvas(self.window, width=1920, height=1015)
        self.canvas.configure(background='black')
        self.set_phrase(self.phrase)
        self.canvas.pack(fill='both', expand=True)

    def set_phrase(self, phrase):
        self.has_celebrated = False
        self.phrase = phrase
        self.fill_closed_boxes()
        self.add_phrase()

    def fill_closed_boxes(self):
        for i in range(12):
            for j in range(int(math.floor(1015 / CLOSED_BOX.height()))):
                self.canvas.create_image(i * (int(math.floor(1920 / 12))),
                                         LEFT_OVER_TOP_BOT_MARGIN / 2 + j * CLOSED_BOX.height(), image=CLOSED_BOX,
                                         anchor='nw')

    def add_phrase(self):
        lines = self.distribute_to_lines()
        for row, line in enumerate(lines):
            start_index, string = line
            for i, char in enumerate([*string]):
                if char != ' ':
                    self.canvas.create_image((i + start_index) * (int(math.floor(1920 / 12))),
                                             LEFT_OVER_TOP_BOT_MARGIN / 2 + (row + 1) * OPEN_BOX.height(),
                                             image=OPEN_BOX,
                                             anchor='nw')

    def center_on_line(self, line):
        res_string = ' '.join(line)
        start_index = 6 - math.ceil((len(res_string) / 2))
        return start_index, res_string

    def add_char_box(self, pred_char):
        lines = self.distribute_to_lines()
        for row, line in enumerate(lines):
            start_index, string = line
            for i, char in enumerate([*string]):
                if char == pred_char:
                    self.canvas.create_text(
                        (i + start_index) * (int(math.floor(1920 / 12))) + math.floor(0.5 * OPEN_BOX.width()),
                        LEFT_OVER_TOP_BOT_MARGIN / 2 + (row + 1) * OPEN_BOX.height() + math.floor(
                            0.5 * OPEN_BOX.height() - 10), text=char,
                        fill="black", font='Kiona 120')

    def distribute_to_lines(self):
        lines = []
        current_line = []
        words = self.phrase.split(' ')
        for word in words:
            if not (sum(list(map(lambda x: len(x) + 1, current_line))) + len(word) <= 10):
                lines.append(current_line)
                current_line = []
            current_line.append(word)
        lines.append(current_line)
        return list(map(lambda x: self.center_on_line(x), lines))

    def keydown(self, e):
        if e.keysym == 'space':
            self.show_phrase()

    def add_char_to_guessed(self, char):
        self.guessed_characters.append(char)
        self.guessed_characters = list(set(self.guessed_characters))
        if ' ' in self.guessed_characters:
            self.guessed_characters.remove(' ')

    def keyup(self, e):
        pred_char = e.char.upper()
        if pred_char in LEGAL_CHARACTERS and pred_char in self.phrase and pred_char not in self.guessed_characters:
            self.add_char_box(pred_char)
            self.add_char_to_guessed(pred_char)
            music = AudioSegment.from_mp3(resource_path("ding.mp3"))
            play(music)

        if e.keysym == 'Return':
            for char in [*self.phrase]:
                self.add_char_box(char)
                self.add_char_to_guessed(char)

        if e.keysym == 'space':
            self.hide_phrase()

        if len(self.phrase_characters) == len(self.guessed_characters):
            self.victory_mode()

    def victory_mode(self):
        if not self.has_celebrated:
            #self.canvas.create_image(500, 500, image=CONFETTI_CANNON, anchor='nw')
            music = AudioSegment.from_mp3(resource_path("victory.mp3"))
            play(music)
        self.has_celebrated = True


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = PhraseBody(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


class PhraseHeader(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        names = ["Sætning","Kategori", ""]
        frame = tk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)
        for i, title in enumerate(names):
            l = tk.Label(frame, text=title, font='Helvetica 16 bold')
            l.grid(row=0, column=i)
            frame.grid_columnconfigure(i, weight=3)


class PhraseFooter(tk.Frame):
    def __init__(self, parent, body, close):
        tk.Frame.__init__(self, parent)
        self.body = body
        self.close = close
        self.save_db_btn = tk.Button(self, text="Gem", font='Helvetica 16 bold', command=self.save)
        self.save_db_btn.pack()

    def save(self):
        if any(list(map(lambda x: len(x[0].get()) == 0 or len(x[1].get()) == 0, self.body.entries))):
            return
        self.body.refresh_phrases()
        save_db()
        self.close()


class PhraseUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.window = None

    def display(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Raa Lykkehjulet")
        self.window.geometry("900x500")
        self.header = PhraseHeader(self.window)
        self.body = VerticalScrolledFrame(self.window)
        self.footer = PhraseFooter(self.window, self.body.interior, self.close)
        self.header.pack(side="top", fill="both")  # , expand=True)
        self.body.pack(side="top", fill="both", expand=True)
        self.footer.pack(side="top", fill="both")  # , expand=True)

    def close(self):
        self.window.destroy()


class PhraseBody(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.entries = []
        self.buttons = []
        self.columns = 2
        self.refresh_entries()

    def refresh_phrases(self):
        global PHRASES
        temp = []
        for i, (phraseE, categoryE) in enumerate(self.entries):
            temp.append((phraseE.get(), categoryE.get()))
        PHRASES = np.array(temp)

    def refresh_entries(self):
        for i in range(len(self.entries)):
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            self.entries = []
        if len(PHRASES) > 0:
            for phrase, category in PHRASES:
                self.add_row(phrase, category)
        else:
            self.add_row("", "")

    def delete_row(self, i):
        if len(self.entries) > 1:
            for (phraseE, categoryE) in self.entries:
                categoryE.grid_forget()
                phraseE.grid_forget()
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            del self.entries[i - 1]
            for i, (phraseE, categoryE) in enumerate(self.entries):
                button_frame = self.button_frame(i + 1)
                self.buttons.append(button_frame)
                phraseE.grid(row=i, column=0, stick="nsew")
                categoryE.grid(row=i, column=1, stick="nsew")
                button_frame.grid(row=i, column=2, stick="nsew")

    def button_frame(self, i):
        button_frame = tk.Frame(self)
        delete = tk.Button(button_frame, text=" - ", command=lambda: self.delete_row(i))
        add = tk.Button(button_frame, text=" + ", command=lambda: self.add_row("", ""))
        delete.pack(side="left")
        add.pack(side="left")
        return button_frame

    def add_row(self, phrase, category):
        phraseE = tk.Entry(self, validate="key")
        phraseE.insert(0, phrase)
        categoryE = tk.Entry(self, validate="key")
        categoryE.insert(0, category)
        self.entries.append((phraseE, categoryE))
        for button_frame in self.buttons:
            button_frame.grid_forget()
        self.buttons = []
        for i, (phraseE, categoryE) in enumerate(self.entries):
            button_frame = self.button_frame(i + 1)
            self.buttons.append(button_frame)
            phraseE.grid(row=i, column=0, stick="nsew")
            categoryE.grid(row=i, column=1, stick="nsew")
            button_frame.grid(row=i, column=2, stick="nsew")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=3)


class RootWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Raa Lykkehjulet")
        self.frame = tk.Frame(self.root, width=30, height=0)
        self.frame.pack()
        self.frame.focus_set()
        self.frame.bind("<KeyPress>", self.keydown)
        self.frame.bind("<KeyRelease>", self.keyup)

        self.phrase, self.category = random.choice(PHRASES)
        self.phrase_var = tk.StringVar()
        self.phrase_var.set(self.category)
        self.solved_phrase_btn = tk.Button(self.root, textvariable=self.phrase_var, height=1, width=30)
        self.solved_phrase_btn.config(state=tk.DISABLED)

        self.phrase_table_window = PhraseUI(self.root)
        self.phrase_table_btn = tk.Button(self.root, text="Åben sætningstabel", height=1, width=30, command=self.open_phrase_table)

        self.gameWindow = GameWindow(self.root, self.phrase, self.display_phrase, self.hide_phrase)
        self.game_window_btn = tk.Button(self.root,
                             text="Åben spilvindue",
                             command=self.generate_new_phrase, height=1, width=30)
        self.game_window_btn.pack()
        self.phrase_table_btn.pack()
        self.solved_phrase_btn.pack()

    def open_phrase_table(self):
        if self.phrase_table_window.window is None or not self.phrase_table_window.window.winfo_exists():
            self.phrase_table_window.display()

    def generate_new_phrase(self):
        self.phrase, self.category = random.choice(PHRASES)
        if self.gameWindow.window is None or not self.gameWindow.window.winfo_exists():
            self.gameWindow.display()
        else:
            self.gameWindow.set_phrase(self.phrase)
            self.phrase_var.set(self.category)

    def mainloop(self):
        self.root.mainloop()

    def keydown(self, e):
        if e.keysym == 'space':
            self.display_phrase()

    def display_phrase(self):
        self.phrase_var.set(self.phrase)

    def hide_phrase(self):
        self.phrase_var.set(self.category)

    def keyup(self, e):
        if e.keysym == 'space':
            self.hide_phrase()
        if self.gameWindow.window is not None and self.gameWindow.window.winfo_exists():
            self.gameWindow.keyup(e)


SAVE_PATH = os.path.join(userpaths.get_my_documents(), 'Lykkehjulet')
LEGAL_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'Æ', 'Ø', 'Å']
PHRASES = np.array([('BAMSE ER FRA JYLLAND', "RANDOM")])
load_db()

root = RootWindow()
cbi = Image.open(resource_path("closed-box.jpg"))
cbi_resized = cbi.resize((int(math.floor(1920 / 12)), int(math.floor((cbi.height / cbi.width) * 1920 / 12))))
CLOSED_BOX = ImageTk.PhotoImage(cbi_resized)

obi = Image.open(resource_path("open-box.jpg"))
obi_resized = obi.resize((int(math.floor(1920 / 12)), int(math.floor((obi.height / obi.width) * 1920 / 12))))
OPEN_BOX = ImageTk.PhotoImage(obi_resized)

LEFT_OVER_TOP_BOT_MARGIN = 1015 - (int(math.floor(1015 / CLOSED_BOX.height())) * CLOSED_BOX.height())

cc = Image.open(resource_path("confetti-cannon.gif"))
cc_resized = cc.resize((1920, int(math.floor((obi.height / obi.width) * 1920))))
CONFETTI_CANNON = ImageTk.PhotoImage(cc_resized)
root.mainloop()
