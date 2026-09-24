from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Horizontal
from collections import Counter
import random
import os
import sys
import pyfiglet

banner = pyfiglet.figlet_format("TERMDLE", font="big")

def getResourcePath(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def loadWordfile(filename):
    try:
        file_path = getResourcePath(filename)
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return [
                line.strip().upper()
                for line in file
                if len(line.strip()) == 5
            ]
    except FileNotFoundError:
        return []
    
Target = loadWordfile("wordslist.txt")
validGuesses = set(loadWordfile("allowedGuesses.txt"))

if not validGuesses:
    validGuesses = set(Target)
else:
    validGuesses.update(Target)

def validate(guess: str, target: str):
    lettersCount = Counter(target)
    result = [None] * len(guess)
    index = 0
    pos = 0
    for char in guess:
        if char not in target:
            result[index] = f"Gray {char}"
            index += 1
            continue
        if char == target[index] and lettersCount[char] > 0:
            lettersCount[char] -= 1
            result[index] = f"Green {char}"
        index += 1
    for letter in result:
        char = guess[pos]
        if letter is None:
            if lettersCount[char] > 0:
                lettersCount[char] -= 1
                result[pos] = f"Yellow {char}"
            else:
                result[pos] = f"Gray {char}"
        pos += 1
    return result

class Tile(Static):
    def __init__(self, letter="", status="gray"):
        super().__init__(letter, classes=f"tile tile-{status}")

class HorizontalTiles(Horizontal):
    def __init__(self, result=None):
        super().__init__()
        self.result = result or []

    def compose(self):
        if not self.result:
            for _ in range(5):
                yield Tile("", "gray")
        else:
            for entry in self.result:
                status, letter = entry.split()
                yield Tile(letter, status.lower())

class TermdleApp(App):
    BINDINGS = [
        ("ctrl+r", "restart", "Restart"),
        ("ctrl+c", "quit", "Quit"),
    ]
    def action_restart(self) -> None:
        self.target = random.choice(Target)
        self.guesses_left = 6
        for row in self.rows:
            row.remove_children()
            for _ in range(5):
                row.mount(Tile("", "gray"))
        self.query_one("#message", Static).update("Guess the 5-letter word!")
        guess_input = self.query_one("#guess-input", Input)
        guess_input.disabled = False
        guess_input.value = ""
    
    CSS_PATH = "termdle.css"

    def compose(self) -> ComposeResult:
        self.target = random.choice(Target)
        self.guesses_left = 6
        self.rows = []
        yield Static(banner, id="intro")
        yield Static("Guess the 5-letter word!", id="message")
        for _ in range(6):
            row = HorizontalTiles()
            self.rows.append(row)
            yield row
        yield Input(placeholder="Type your guess...", id="guess-input", max_length=5)
        yield Static("Made by Nostromis\n ctrl + r restart | ctrl + c quit", id="credits")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        guess = event.value.upper()
        message = self.query_one("#message", Static)

        if len(guess) != 5:
            message.update("Guess must be 5 letters.")
            return

        if guess not in validGuesses:
            message.update("Not a valid word in the dictionary!")
            return
    
        result = validate(guess, self.target)
        current_row = self.rows[6 - self.guesses_left]
        current_row.remove_children()
        for entry in result:
            status, letter = entry.split()
            current_row.mount(Tile(letter, status.lower()))

        if all(entry.startswith("Green") for entry in result):
            message.update(f"You win! The word was {self.target}.")
            event.input.disabled = True
            return

        self.guesses_left -= 1
        if self.guesses_left <= 0:
            message.update(f"Out of guesses. The word was {self.target}.")
            event.input.disabled = True
            return

        event.input.value = ""

if __name__ == "__main__":
    app = TermdleApp()
    app.run()