import turtle
import time
import random
from enum import Enum, auto as enum_auto
from turtle import Turtle
from typing import Union

DEFAULT_SQUARE_SIDE = 21
DEFAULT_CIRCLE_DIAMETER = 21
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DEFAULT_SNAKE_LEN = 6
DEFAULT_SNAKE_DELAY = 0.08
SNAKE_DELAY_INCREMENT = 0.01
SCORE_FONT = "Arial"
SCORE_SIZE = 18
SCORE_TYPE = "bold"


class Direction(Enum):
    RIGHT = 0
    UP = 90
    LEFT = 180
    DOWN = 270
    EAST = 0
    NORTH = 90
    WEST = 180
    SOUTH = 270


class ArrowKey(Enum):
    RIGHT = "Right"
    UP = "Up"
    LEFT = "Left"
    DOWN = "Down"


class WASDKey(Enum):
    RIGHT = "d"
    UP = "w"
    LEFT = "a"
    DOWN = "s"


class KeysMode(Enum):
    ARROWS = enum_auto()
    WASD = enum_auto()


class Food(Turtle):
    def __init__(self, position: Union[tuple[float, float], None] = None, shape: str = "circle", color: str = "blue") -> None:
        super().__init__(shape=shape, visible=False)
        self.color(color)
        self.penup()
        position = position if position else self.__rand_position()
        self.goto(position)
        self.showturtle()

    @staticmethod
    def __rand_position(screen_width: int = SCREEN_WIDTH,
                        screen_height: int = SCREEN_HEIGHT) -> tuple[int, int]:
        left = -screen_width//2 + DEFAULT_CIRCLE_DIAMETER
        right = screen_width//2 - DEFAULT_CIRCLE_DIAMETER
        down = -screen_height//2 + DEFAULT_CIRCLE_DIAMETER
        up = screen_height//2 - DEFAULT_CIRCLE_DIAMETER
        return (random.randint(left, right), random.randint(down, up))

    def refresh(self) -> None:
        self.hideturtle()
        self.goto(self.__rand_position())
        self.showturtle()


class Score(Turtle):
    def __init__(self) -> None:
        super().__init__(visible=False)
        self.score = 0
        self.__setup_text()

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, score: int) -> None:
        if not isinstance(score, int):
            raise TypeError
        if score < 0:
            raise ValueError
        self._score = score

    def __str__(self):
        return str(self.score)

    def __add__(self, score: int):
        self.increment(score)
        return self

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, type(self)):
            return super().__eq__(__o)
        elif isinstance(__o, int):
            return self.score == __o
        else:
            raise TypeError

    def __setup_text(self) -> None:
        self.penup()
        self.setpos((0, SCREEN_HEIGHT//2 - 2 * SCORE_SIZE))
        self.color("white")
        self.__write_score()

    def __write_score(self) -> None:
        self.write(arg=self.score, font=(SCORE_FONT, SCORE_SIZE, SCORE_TYPE))

    def get_score(self) -> int:
        return self.score

    def increment(self, inc: int = 1) -> int:
        self.score += inc
        self.clear()
        self.__write_score()
        return self.score

    def game_over(self) -> None:
        self.goto(0, 0)
        self.write(arg="GAME OVER", align='center', font=(SCORE_FONT, SCORE_SIZE, SCORE_TYPE))


class Snake:
    def __init__(self, length: int = DEFAULT_SNAKE_LEN) -> None:
        if not isinstance(length, int):
            raise TypeError
        if length <= 1:
            raise ValueError
        self.__body = [Snake.__create_body_part((-i*DEFAULT_SQUARE_SIDE, 0))
                       for i in range(length)]
        self.head.color("light steel blue")
        self.__delay = DEFAULT_SNAKE_DELAY

    @staticmethod
    def __create_body_part(pos: tuple[int, int], heading: Direction = Direction.RIGHT) -> Turtle:
        new_part = Turtle(shape="square")
        new_part.speed(0)
        new_part.penup()
        new_part.goto(pos)
        new_part.setheading(heading.value)
        new_part.color("white")
        return new_part

    @property
    def head(self) -> Turtle:
        return self.__body[0]

    @property
    def tail(self) -> Turtle:
        return self.__body[-1]

    @property
    def length(self) -> int:
        return len(self.__body)

    def heading(self) -> Direction:
        return Direction(self.head.heading())

    def tail_heading(self) -> Direction:
        return Direction(self.tail.heading())

    def speed_up(self) -> None:
        self.__delay -= SNAKE_DELAY_INCREMENT

    def slow_down(self) -> None:
        self.__delay += SNAKE_DELAY_INCREMENT

    def forward(self) -> None:
        for i in range(self.length-1, 0, -1):
            self.__body[i].goto(self.__body[i-1].xcor(),
                                self.__body[i-1].ycor())
        self.head.forward(DEFAULT_SQUARE_SIDE)
        time.sleep(DEFAULT_SNAKE_DELAY)

    def set_heading(self, direction: Direction) -> None:
        if not isinstance(direction, Direction):
            raise TypeError
        self.head.setheading(direction.value)

    def turn_right(self) -> None:
        self.set_heading(Direction.RIGHT)

    def turn_up(self) -> None:
        self.set_heading(Direction.UP)

    def turn_left(self) -> None:
        self.set_heading(Direction.LEFT)

    def turn_down(self) -> None:
        self.set_heading(Direction.DOWN)

    def grow_up(self,) -> int:
        new_part = Snake.__create_body_part(
            (self.tail.xcor(), self.tail.ycor()))
        self.__body.append(new_part)
        return self.length

    def ate(self, food: Food) -> bool:
        assert food.shape() == 'circle'
        assert self.head.shape() == 'square'
        dist = self.head.distance(food)
        self_dist_from_center = self.head.shapesize()[
            0] * DEFAULT_SQUARE_SIDE * 0.5
        food_dist_from_center = food.shapesize(
        )[0] * DEFAULT_CIRCLE_DIAMETER * 0.5
        return dist <= food_dist_from_center + self_dist_from_center

    def collided_the_wall(self) -> bool:
        if not -SCREEN_WIDTH // 2 + DEFAULT_SQUARE_SIDE < self.head.xcor() <\
                SCREEN_WIDTH // 2 - DEFAULT_SQUARE_SIDE:
            return True
        if not -SCREEN_HEIGHT // 2 + DEFAULT_SQUARE_SIDE < self.head.ycor() <\
                SCREEN_HEIGHT // 2 - DEFAULT_SQUARE_SIDE:
            return True
        return False

    def collided_the_tail(self) -> bool:
        for part in self.__body[1:]:
            if self.head.distance(part) < DEFAULT_SQUARE_SIDE // 2:
                return True
        return False


class GameScreen(turtle._Screen):
    def __init__(self, width: int | float = 768, height: int | float = 648, startx: int | None = None,
                 starty: int | None = None, bgcolor: str | tuple[int, int, int] = "white", colormode: int | float = 255):
        super().__init__()
        turtle.TurtleScreen.__init__(self, GameScreen._canvas)
        if Turtle._screen is None:
            Turtle._screen = self
        self.title("Snake")
        self.setup(width=width, height=height, startx=startx, starty=starty)
        self.screensize(canvwidth=width-10, canvheight=height-10)
        if isinstance(bgcolor, tuple):
            self.colormode(255)
        self.bgcolor(bgcolor)
        self.colormode(colormode)
        self.cv._rootwindow.resizable(False, False)

    def bind_control_keys(self, snake: Snake, mode: KeysMode = KeysMode.ARROWS, escape: str = "space") -> None:
        if not all(isinstance(a, c) for a, c in
                   zip((snake, mode, escape), (Snake, KeysMode, str))):
            raise TypeError
        self.listen()
        dir_mode = ArrowKey if mode is KeysMode.ARROWS else WASDKey
        self.onkeypress(fun=snake.turn_right, key=dir_mode.RIGHT.value)
        self.onkeypress(fun=snake.turn_up, key=dir_mode.UP.value)
        self.onkeypress(fun=snake.turn_left, key=dir_mode.LEFT.value)
        self.onkeypress(fun=snake.turn_down, key=dir_mode.DOWN.value)
        self.onkeypress(fun=self.bye, key=escape)


def main():
    game_screen = GameScreen(
        width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bgcolor='black')
    game_screen.tracer(0)
    snake = Snake()
    food = Food()
    score = Score()
    game_screen.bind_control_keys(snake)
    # main loop:
    while True:
        snake.forward()
        game_screen.update()
        if snake.ate(food):
            #winsound.PlaySound('mixkit-human-male-enjoy-humm-129.wav', winsound.SND_ASYNC)
            snake.grow_up()
            score += 1
            food.refresh()
        elif snake.collided_the_wall() or snake.collided_the_tail():
            score.game_over()
            break

    turtle.done()
    exit(0)


if __name__ == "__main__":
    main()
