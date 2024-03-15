# Sprawl Runner

[![PyPI - Version](https://img.shields.io/pypi/v/sprawl-runner.svg)](https://pypi.org/project/sprawl-runner)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sprawl-runner.svg)](https://pypi.org/project/sprawl-runner)

-----

Sprawl Runner is a riff on a retro text-based adventure game, with a modern twist–it uses ChatGPT to run the narrative of the game.

> Yesterday, you were merely a shadow in the digital wake of your mentor, a Console Cowboy who navigated the matrix with unparalleled dexterity. But today, the streets whisper his name in past tense, leaving behind nothing but echoes and a warning: you might be next on the hit list. With a countdown ticking away before your history comes hunting for you, the sprawl of Night City becomes a neon-lit labyrinth of survival.
>
> Your mission? Amass enough credits to vanish before the sun sets on your escape plans. The jobs? They're there, hidden in the data streams and encrypted whispers, each a gamble between fortune and oblivion. But the city is alive with more than just opportunity; adversarial factions move in the shadows, Turing cops patrol the digital frontier with cold logic, and deadly ICE lurks behind every data heist, ready to flatline your future.
>
> In this race against time, alliances are as fragile as code, and trust is a commodity more valuable than the data you steal. Navigate the underbelly of Night City, decipher the conspiracies that thread through its core, and maybe, just maybe, you'll outpace the specter of your past. But remember, in Night City, everyone's running from something, and the only way out is through.

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install sprawl-runner
```

## License

`sprawl-runner` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

-----

## Developer Notes

Because I will likely forget these things if I don't jot them down now...

### Local dev dir (WSL)

```text
/home/rgroves/sprawl-runner
```

This is my first time using hatch, so after some exploring its usages I want to note some of the cli things I want to remember:

### Start a shell with an active virtual environment

```shell
hatch shell
```

### Show dependencies

```shell
# show both env and project dependencies
hatch dep show table

# show only env dependencies
hatch dep show table -e

# show only project dependencies
hatch dep show table -p
```

### Run linting and formatting

```shell
hatch fmt
```

### Run tests

```shell
# run tests using current environement
hatch run test

# run tests for all compatible environments
hatch run all:test
```

### Run mypy type checks

```shell
hatch run types:check
```
