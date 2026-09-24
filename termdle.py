from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Horizontal
from collections import Counter
import random
import json
import os
from pathlib import Path
import sys
import pyfiglet

banner = pyfiglet.figlet_format("TERMDLE", font="big")

def getStatsPath():
    if os.name == "nt":
        statsDir = Path(os.environ.get("APPDATA", Path.home())) / "termdle"
    else:
        statsDir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "termdle"

    statsDir.mkdir(parents=True, exist_ok=True)
    return statsDir / "stats.json"

def loadStats():
    statsPath = getStatsPath()

    if not statsPath.exists():
        return {
            "score": 0,
            "wins": 0,
            "streak": 0
        }

    try:
        with open(statsPath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {
            "score": 0,
            "wins": 0,
            "streak": 0
        }

def saveStats(stats):
    statsPath = getStatsPath()

    with open(statsPath, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4)

stats = loadStats()
wins = stats["wins"]
streak = stats["streak"]
score = stats["score"]

def getResourcePath(relativePath):
    if hasattr(sys, "_MEIPASS"):
        basePath = Path(sys._MEIPASS)
    else:
        basePath = Path(__file__).resolve().parent
    return basePath / relativePath

def loadWordfile(filename):
    try:
        filePath = getResourcePath(filename)
        with open(filePath, "r", encoding="utf-8-sig") as file:
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

def calculateScore(guessesUsed):
    return round((7 - guessesUsed) / 6 * 100)

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
        self.guessesLeft = 6
        for row in self.rows:
            row.remove_children()
            for _ in range(5):
                row.mount(Tile("", "gray"))
        self.query_one("#message", Static).update("Guess the 5-letter word!")
        guessInput = self.query_one("#guess-input", Input)
        guessInput.disabled = False
        guessInput.value = ""
        guessInput.focus()

    CSS_PATH = str(getResourcePath("termdle.css"))

    def compose(self) -> ComposeResult:
        self.target = random.choice(Target)
        self.guessesLeft = 6
        self.rows = []
        yield Static(f"Wins: {stats['wins']} | Streak: {stats['streak']} | Score: {stats['score']}", id="stats")
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
        current_row = self.rows[6 - self.guessesLeft]
        current_row.remove_children()
        for entry in result:
            status, letter = entry.split()
            current_row.mount(Tile(letter, status.lower()))

        if all(entry.startswith("Green") for entry in result):
            message.update(f"You win! The word was {self.target}.")
            event.input.disabled = True
            guesses_used = 6 - self.guessesLeft + 1
            stats["wins"] += 1
            stats["streak"] += 1
            stats["score"] += calculateScore(guesses_used)
            saveStats(stats)
            self.query_one("#stats", Static).update(f"Wins: {stats['wins']} | Streak: {stats['streak']} | Score: {stats['score']}")
            return

        self.guessesLeft -= 1
        if self.guessesLeft <= 0:
            message.update(f"Out of guesses. The word was {self.target}.")
            event.input.disabled = True
            stats["streak"] = 0
            saveStats(stats)
            self.query_one("#stats", Static).update(f"Wins: {stats['wins']} | Streak: {stats['streak']} | Score: {stats['score']}")
            return

        event.input.value = ""

def main():
    TermdleApp().run()

if __name__ == "__main__":
    main()