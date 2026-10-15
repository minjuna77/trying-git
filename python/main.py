"""Terminal Snake. Run: python3 python/main.py (arrows/WASD, P pause, R restart, Q quit)."""

import curses
import random
import time


WIDTH, HEIGHT = 30, 18
DIRECTIONS = {
    curses.KEY_UP: (0, -1), ord("w"): (0, -1),
    curses.KEY_DOWN: (0, 1), ord("s"): (0, 1),
    curses.KEY_LEFT: (-1, 0), ord("a"): (-1, 0),
    curses.KEY_RIGHT: (1, 0), ord("d"): (1, 0),
}


def place_food(snake):
    occupied = set(snake)
    empty = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
             if (x, y) not in occupied]
    return random.choice(empty) if empty else None


def advance(snake, direction, food):
    """Return the next body, food, and outcome without changing the input body."""
    x, y = snake[0]
    dx, dy = direction
    head = (x + dx, y + dy)
    growing = head == food
    body = snake if growing else snake[:-1]
    if not (0 <= head[0] < WIDTH and 0 <= head[1] < HEIGHT) or head in body:
        return snake, food, "Game over!"
    snake = [head] + (snake if growing else snake[:-1])
    if growing:
        food = place_food(snake)
    return snake, food, "You win!" if food is None else ""


def play(screen):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.keypad(True)
    screen.timeout(120)

    def reset():
        body = [(WIDTH // 2 - i, HEIGHT // 2) for i in range(3)]
        return body, (1, 0), place_food(body), False, ""

    snake, direction, food, paused, outcome = reset()
    while True:
        frame_started = time.monotonic()
        screen.erase()
        rows, columns = screen.getmaxyx()
        too_small = rows < HEIGHT + 6 or columns < WIDTH + 2

        def write(y, x, text):
            # Leave the bottom-right cell untouched: curses can raise there.
            if y < rows and x < columns - 1:
                screen.addnstr(y, x, text, columns - x - 1)

        if too_small:
            write(0, 0, f"Resize terminal to {WIDTH + 2} columns x {HEIGHT + 6} rows.")
            write(1, 0, "Q: quit")
        else:
            write(0, 0, f"SNAKE   Score: {len(snake) - 3}")
            write(1, 0, "+" + "-" * WIDTH + "+")
            for y in range(HEIGHT):
                write(y + 2, 0, "|" + " " * WIDTH + "|")
            write(HEIGHT + 2, 0, "+" + "-" * WIDTH + "+")
            if food is not None:
                write(food[1] + 2, food[0] + 1, "*")
            for index, (x, y) in enumerate(snake):
                write(y + 2, x + 1, "@" if index == 0 else "o")
            write(HEIGHT + 3, 0, "Arrows/WASD move | P pause")
            write(HEIGHT + 4, 0, "R restart | Q quit")
            write(HEIGHT + 5, 0, outcome or ("Paused" if paused else "Eat * and avoid walls/yourself."))
        screen.refresh()
        key = screen.getch()
        if 65 <= key <= 90:
            key += 32
        if key == ord("q"):
            return
        if key == ord("r"):
            snake, direction, food, paused, outcome = reset()
            continue
        if too_small or key == curses.KEY_RESIZE:
            continue
        if key in (ord("p"), ord(" ")):
            paused = not paused
            continue
        if paused or outcome:
            continue
        candidate = DIRECTIONS.get(key, direction)
        if candidate != (-direction[0], -direction[1]):
            direction = candidate
        snake, food, outcome = advance(snake, direction, food)
        # Discard queued key repeats so each move keeps its intended pace.
        curses.flushinp()
        curses.napms(max(0, int((0.12 - (time.monotonic() - frame_started)) * 1000)))


def main():
    try:
        curses.wrapper(play)
    except KeyboardInterrupt:
        pass
    except curses.error:
        print("Run this game in an interactive terminal with a supported TERM setting.")


if __name__ == "__main__":
    main()
