# Termdle

A terminal word-guessing game.

![Termdle](https://github.com/Nostromis/Termdle/blob/main/assests/termdle-logo.png)

## What is it?

Termdle is a word-guessing game that runs entirely in the terminal.

You get 6 attempts to guess a randomly selected 5-letter word.

After every guess, the letters are highlighted depending on how they match the target:

- Green = correct letter and position
- Yellow = correct letter, wrong position
- No color = letter isn't in the word

Duplicate letters are also handled correctly when checking guesses.

## Controls

- `Enter` — submit a guess
- `Ctrl + R` — restart the game
- `Ctrl + C` — exit

## Running Termdle

The current version is distributed as a Windows `.exe`, so you don't need Python or any dependencies installed.

Download the latest release from the [Releases](../../releases) page and run it.

# Demo
![DEMO](https://github.com/Nostromis/Termdle/blob/main/assests/playthrough.gif)

## Source

```text
Termdle/
├── termdle.py
├── wordslist.txt
├── validGuesses.txt
└── termdle.css
