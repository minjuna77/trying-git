"""Play Snake with the arrow keys or WASD. Run with: python3 python/main.py."""

import random
import tkinter as tk


CELL = 24
COLUMNS = 25
ROWS = 20
TICK_MS = 110
DIRECTIONS = {
    "Up": (0, -1), "w": (0, -1),
    "Down": (0, 1), "s": (0, 1),
    "Left": (-1, 0), "a": (-1, 0),
    "Right": (1, 0), "d": (1, 0),
}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake")
        root.resizable(False, False)
        self.status = tk.StringVar()
        tk.Label(root, textvariable=self.status, font=("Arial", 14)).pack(pady=8)
        self.canvas = tk.Canvas(
            root, width=COLUMNS * CELL, height=ROWS * CELL,
            background="#101820", highlightthickness=0,
        )
        self.canvas.pack()
        tk.Label(root, text="Arrows / WASD: move    Space: pause    R: restart").pack(pady=8)
        root.bind("<KeyPress>", self.on_key)
        self.reset()
        self.tick()

    def reset(self):
        self.snake = [(COLUMNS // 2 - i, ROWS // 2) for i in range(3)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.turn_queued = False
        self.paused = False
        self.finished = False
        self.food = self.place_food()
        self.draw()

    def place_food(self):
        occupied = set(self.snake)
        empty = [(x, y) for x in range(COLUMNS) for y in range(ROWS)
                 if (x, y) not in occupied]
        return random.choice(empty) if empty else None

    def on_key(self, event):
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key == "r":
            self.reset()
        elif key == "space" and not self.finished:
            self.paused = not self.paused
            self.draw()
        elif key in DIRECTIONS and not (self.finished or self.paused or self.turn_queued):
            direction = DIRECTIONS[key]
            if direction != self.direction and direction != tuple(-n for n in self.direction):
                self.next_direction = direction
                self.turn_queued = True

    def tick(self):
        if not self.finished and not self.paused:
            self.direction = self.next_direction
            self.turn_queued = False
            x, y = self.snake[0]
            dx, dy = self.direction
            head = (x + dx, y + dy)
            growing = head == self.food
            body = self.snake if growing else self.snake[:-1]
            if not (0 <= head[0] < COLUMNS and 0 <= head[1] < ROWS) or head in body:
                self.finished = True
            else:
                self.snake.insert(0, head)
                if growing:
                    self.food = self.place_food()
                    self.finished = self.food is None
                else:
                    self.snake.pop()
            self.draw()
        self.root.after(TICK_MS, self.tick)

    def draw(self):
        self.canvas.delete("all")
        self.status.set(f"Score: {len(self.snake) - 3}")
        for index, (x, y) in enumerate(self.snake):
            self.draw_cell(x, y, "#b5ef8a" if index == 0 else "#69c779")
        if self.food is not None:
            self.draw_cell(*self.food, "#ff6b6b")
        if self.finished or self.paused:
            message = "You win!" if self.food is None else "Game over"
            message = message + " — press R to restart" if self.finished else "Paused"
            self.canvas.create_rectangle(0, ROWS * CELL // 2 - 30,
                                         COLUMNS * CELL, ROWS * CELL // 2 + 30,
                                         fill="#101820", outline="")
            self.canvas.create_text(COLUMNS * CELL // 2, ROWS * CELL // 2,
                                    text=message, fill="white", font=("Arial", 20))

    def draw_cell(self, x, y, color):
        self.canvas.create_rectangle(x * CELL + 1, y * CELL + 1,
                                     (x + 1) * CELL - 1, (y + 1) * CELL - 1,
                                     fill=color, outline="")


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
