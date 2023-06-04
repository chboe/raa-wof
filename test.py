import tkinter as tk
import sys, os
import numpy as np
import random
from PIL import ImageTk, Image
import userpaths
import math


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
    def __init__(self, master, phrase):
        self.displayed = False
        self.phrase = phrase
        self.master = master
        self.window = None

    def display(self):
        self.window = tk.Toplevel(self.master)
        self.window.bind("<KeyRelease>", self.keyup)
        self.window.title("Raa Lykkehjulet")
        self.window.geometry("1920x1015")
        self.window.state('zoomed')
        self.canvas = tk.Canvas(self.window, width=1920, height=1015)
        self.canvas.configure(background='black')
        self.set_phrase(self.phrase)
        self.canvas.pack(fill='both', expand=True)

    def set_phrase(self, phrase):
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
                    self.canvas.create_text((i + start_index) * (int(math.floor(1920 / 12)))+math.floor(0.5*OPEN_BOX.width()),
                                            LEFT_OVER_TOP_BOT_MARGIN / 2 + (row + 1) * OPEN_BOX.height()+math.floor(0.5*OPEN_BOX.height()-10), text=char,
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

    def keyup(self, e):
        pred_char = e.char.upper()
        if pred_char in LEGAL_CHARACTERS and pred_char in self.phrase:
            self.add_char_box(pred_char)

        if e.keysym == 'Return':
            for char in [*self.phrase]:
                self.add_char_box(char)


class RootWindow:
    def __init__(self):

        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, width=500, height=500)
        self.frame.pack()
        self.frame.focus_set()
        self.frame.bind("<KeyRelease>", self.keyup)
        self.phrase = random.choice(PHRASES)
        self.gameWindow = GameWindow(self.root, self.phrase)
        self.btn = tk.Button(self.root,
                             text="Click to open a new window",
                             command=self.generate_new_phrase)

        self.entries = []
        self.buttons = []
        self.columns = 2
        self.refresh_entries()
        #self.btn.pack()

    def refresh_entries(self):
        for i in range(len(self.entries)):
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            self.entries = []
        if len(PHRASES) > 0:
            for phrase in PHRASES:
                self.add_row(phrase)
        else:
            self.add_row("")

    def delete_row(self, i):
        if len(self.entries) > 1:
            for phraseE in self.entries:
                phraseE.grid_forget()
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            del self.entries[i - 1]
            for i, phraseE in enumerate(self.entries):
                button_frame = self.button_frame(i + 1)
                self.buttons.append(button_frame)
                phraseE.grid(row=i, column=0, stick="nsew")
                button_frame.grid(row=i, column=1, stick="nsew")

    def button_frame(self, i):
        button_frame = tk.Frame(self.frame)
        delete = tk.Button(button_frame, text=" - ", command=lambda: self.delete_row(i))
        add = tk.Button(button_frame, text=" + ", command=lambda: self.add_row(i))
        delete.pack(side="left")
        add.pack(side="left")
        return button_frame

    def add_row(self, phrase):
        phraseE = tk.Entry(self.frame, validate="key")
        phraseE.insert(0, phrase)
        self.entries.append(phraseE)
        for button_frame in self.buttons:
            button_frame.grid_forget()
        self.buttons = []
        for i, phraseE in enumerate(self.entries):
            button_frame = self.button_frame(i + 1)
            self.buttons.append(button_frame)
            phraseE.grid(row=i, column=0, stick="nsew")
            button_frame.grid(row=i, column=1, stick="nsew")

    def generate_new_phrase(self):
        self.phrase = random.choice(PHRASES)
        if self.gameWindow.window is None or not self.gameWindow.window.winfo_exists():
            self.gameWindow.display()
        else:
            self.gameWindow.set_phrase(self.phrase)

    def mainloop(self):
        self.root.mainloop()

    def keyup(self, e):
        if self.gameWindow.window is not None and self.gameWindow.window.winfo_exists():
            self.gameWindow.keyup(e)


SAVE_PATH = os.path.join(userpaths.get_my_documents(), 'Lykkehjulet')
LEGAL_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'Æ', 'Ø', 'Å']
PHRASES = np.array(['BAMSE ELSKER SODAVANDEN'])

root = RootWindow()

cbi = Image.open(resource_path("closed-box.jpg"))
cbi_resized = cbi.resize((int(math.floor(1920 / 12)), int(math.floor((cbi.height / cbi.width) * 1920 / 12))))
CLOSED_BOX = ImageTk.PhotoImage(cbi_resized)

obi = Image.open(resource_path("open-box.jpg"))
obi_resized = obi.resize((int(math.floor(1920 / 12)), int(math.floor((obi.height / obi.width) * 1920 / 12))))
OPEN_BOX = ImageTk.PhotoImage(obi_resized)

LEFT_OVER_TOP_BOT_MARGIN = 1015 - (int(math.floor(1015 / CLOSED_BOX.height())) * CLOSED_BOX.height())

root.mainloop()
