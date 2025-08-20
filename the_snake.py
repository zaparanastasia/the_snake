from random import choice, randint
import pygame

# --- Константы ---
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = (SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
          SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
OPPOSITE_DIRECTIONS = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self, position, color):
        self.position = position
        self.body_color = color

    def draw_cell(self, position):
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied):
        super().__init__((0, 0), APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied):
        while True:
            pos = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                   randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if pos not in occupied:
                self.position = pos
                break

    def draw(self):
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        super().__init__(CENTER, SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self, new_dir):
        if new_dir and new_dir != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_dir

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)
        self.last = self.positions.pop() if len(self.positions) > self.length else None

    def draw(self):
        self.draw_cell(self.get_head_position())
        if self.last:
            # закрасить хвост
            rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def reset(self):
        self.length = 1
        self.positions = [CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(snake):
    new_direction = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                new_direction = UP
            elif event.key == pygame.K_DOWN:
                new_direction = DOWN
            elif event.key == pygame.K_LEFT:
                new_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                new_direction = RIGHT

    snake.update_direction(new_direction)


def main():
    snake = Snake()
    apple = Apple(set(snake.positions))
    speed = SPEED
    max_length = 1

    while True:
        clock.tick(speed)

        handle_keys(snake)
        snake.move()

        # Проверка на самоукус
        if snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(set(snake.positions))
            speed = SPEED
            max_length = 1
            continue

        # Проверка на яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(set(snake.positions))
            speed += 1

        snake.draw()
        apple.draw()

        max_length = max(max_length, snake.length)

        pygame.display.set_caption(
            f'Змейка | ESC - выход | Скорость: {speed} | Рекорд длины: {max_length}'
        )
        pygame.display.update()


if __name__ == '__main__':
    main()
