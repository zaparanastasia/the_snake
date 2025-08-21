"""Classic Snake game implemented with OOP and pygame.

This module defines three classes:
- GameObject: base class with common drawing helpers.
- Apple: food that appears at random free cells.
- Snake: the player-controlled snake.

It also contains the main game loop with input handling and game rules.

PEP 8 compliant, with docstrings for public callables.
"""
from __future__ import annotations

from random import choice
from typing import Iterable, Optional, Set, Tuple

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER: Tuple[int, int] = (
    (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
    (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE,
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED_START = 20

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()

Coord = Tuple[int, int]


def wrap_to_screen(x: int, y: int) -> Coord:
    """Return coordinates wrapped around the screen edges to create torus space."""
    return x % SCREEN_WIDTH, y % SCREEN_HEIGHT


def build_occupied(snake_positions: Iterable[Coord], apple_pos: Optional[Coord] = None) -> Set[Coord]:
    """Return a set of currently occupied cells (snake + optional apple)."""
    occ: Set[Coord] = set(snake_positions)
    if apple_pos is not None:
        occ.add(apple_pos)
    return occ


class GameObject:
    """Base class for game objects with a position and color."""

    def __init__(self, position: Coord, color: Tuple[int, int, int]):
        """Initialize object with *position* (top-left pixel of a cell) and *color*."""
        self.position: Coord = position
        self.body_color: Tuple[int, int, int] = color

    def draw(self) -> None:
        """Draw the object. Subclasses must implement their own drawing."""

    def draw_cell(self, position: Coord, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a single cell at *position* using *color* or self.body_color."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color or self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Apple object that spawns in a random free cell."""

    def __init__(self, occupied: Set[Coord]):
        """Create an apple and place it at a free random cell not in *occupied*."""
        super().__init__(CENTER, APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied: Set[Coord]) -> None:
        """Place the apple at a random free cell, avoiding *occupied* positions."""
        free: list[Coord] = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied
        ]
        if free:
            self.position = free[choice(range(len(free)))]

    def draw(self) -> None:
        """Draw the apple as a filled square cell."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Player-controlled snake with grid-based movement."""

    def __init__(self) -> None:
        """Construct the snake and reset it to the initial state."""
        super().__init__(CENTER, SNAKE_COLOR)
        self.reset()

    def get_head_position(self) -> Coord:
        """Return the current head position (first element of body list)."""
        return self.positions[0]

    def update_direction(self, new_direction: Coord) -> None:
        """Update direction if *new_direction* isn't opposite to current one."""
        if new_direction != OPPOSITE[self.direction]:
            self.direction = new_direction

    def move(self) -> None:
        """Advance the snake by one cell in the current direction."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = wrap_to_screen(head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)
        self.positions.insert(0, new_head)
        self.last = self.positions.pop() if len(self.positions) > self.length else None

    def draw(self) -> None:
        """Draw the head and erase the trailing cell, if any."""
        self.draw_cell(self.get_head_position())
        if self.last is not None:
            rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def reset(self) -> None:
        """Reset the snake to initial state at the screen center."""
        self.length: int = 1
        self.positions: list[Coord] = [CENTER]
        self.direction: Coord = choice([UP, DOWN, LEFT, RIGHT])
        self.last: Optional[Coord] = None


def handle_keys(snake: Snake) -> None:
    """Process pygame events and steer the snake or exit the game."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,):
                pygame.quit()
                raise SystemExit
            if event.key == pygame.K_UP:
                snake.update_direction(UP)
            elif event.key == pygame.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pygame.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pygame.K_RIGHT:
                snake.update_direction(RIGHT)


def main() -> None:
    """Run the Snake game main loop."""
    snake = Snake()
    occupied = build_occupied(snake.positions)
    apple = Apple(occupied)

    speed = SPEED_START
    best_length = snake.length

    while True:
        clock.tick(speed)

        handle_keys(snake)
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            speed = SPEED_START
            best_length = max(best_length, 1)
            occupied = build_occupied(snake.positions)
            apple.randomize_position(occupied)
        else:
            if snake.get_head_position() == apple.position:
                snake.length += 1
                best_length = max(best_length, snake.length)
                occupied = build_occupied(snake.positions)
                apple.randomize_position(occupied)
            snake.draw()
            apple.draw()

        pygame.display.set_caption(
            f"Змейка | ESC — выход | Скорость: {speed} | Рекорд длины: {best_length}"
        )
        pygame.display.update()

        speed = SPEED_START + (snake.length - 1)


if __name__ == "__main__":
    main()
