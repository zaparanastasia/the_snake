"""Игра Змейка"""

from random import choice, randint
import pygame


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

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

    def __init__(self, position=None, color=None):
        """Инициализация объекта с позицией и цветом."""
        self.position = position
        self.body_color = color

    def draw_cell(self, position):
        """Отрисовать одну ячейку объекта."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        """Создает яблоко в случайной позиции."""
        super().__init__(self.randomize_position(), APPLE_COLOR)

    def randomize_position(self):
        """Случайная позиция яблока на сетке."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)
        return self.position

    def draw(self):
        """Отрисовка яблока."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализация змейки в центре экрана."""
        center = ((SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
                  (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE)
        super().__init__(center, SNAKE_COLOR)
        self.length = 1
        self.positions = [center]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.max_length = 1

    def get_head_position(self):
        """Возвращает позицию головы змеи."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змеи."""
        if self.next_direction:
            opposite = (-self.direction[0], -self.direction[1])
            if self.next_direction != opposite:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Передвигает змейку по полю."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        if new_head in self.positions[1:]:
            self.reset()
        else:
            self.positions.insert(0, new_head)
            if len(self.positions) > self.length:
                self.last = self.positions.pop()
            else:
                self.last = None
            self.max_length = max(self.max_length, self.length)

    def draw(self):
        """Отрисовка головы и хвоста змеи."""
        self.draw_cell(self.positions[0])
        if self.last:
            rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        center = ((SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
                  (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE)
        self.positions = [center]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None
        self.max_length = 1


def handle_keys(snake):
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Главная функция игры."""
    snake = Snake()
    apple = Apple()
    speed = SPEED
    while True:
        clock.tick(speed)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            # динамика: ускоряемся при съедении яблока
            speed += 1

        snake.draw()
        apple.draw()

        # Обновляем заголовок
        pygame.display.set_caption(
            'Змейка | ESC - выход | Скорость: {} | Рекорд длины: {}'.format(
                speed, snake.max_length
            )
        )
        pygame.display.update()


if __name__ == '__main__':
    main()
