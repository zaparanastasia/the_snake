from random import choice, randint
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
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

    def __init__(self, color=None):
        self.body_color = color

    def draw_cell(self, position):
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions=None):
        super().__init__(APPLE_COLOR)
        self.position = None
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        while True:
            pos = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                   randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if not occupied_positions or pos not in occupied_positions:
                self.position = pos
                break

    def draw(self):
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self, new_direction=None):
        if new_direction and new_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_direction

    def move(self):
        new_head = ((self.get_head_position()[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
                    (self.get_head_position()[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, new_head)
        self.last = self.positions.pop() if len(self.positions) > self.length else None

    def draw(self):
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(self.last)

    def reset(self):
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(snake):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_UP:
                snake.update_direction(UP)
            elif event.key == pygame.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pygame.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pygame.K_RIGHT:
                snake.update_direction(RIGHT)


def main():
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    speed = SPEED
    max_length = snake.length

    while True:
        clock.tick(speed)

        handle_keys(snake)
        snake.move()

        # Проверка на самоукус
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Яблоко съедено
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)
            speed += 1

        max_length = max(max_length, snake.length)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()

        pygame.display.set_caption(
            f'Змейка | ESC - выход | Скорость: {speed} | Рекорд длины: {max_length}'
        )
        pygame.display.update()


if __name__ == '__main__':
    main()
