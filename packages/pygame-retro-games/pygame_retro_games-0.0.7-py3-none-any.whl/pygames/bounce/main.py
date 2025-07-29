import math
import os

import numpy
import pygame
import asyncio


class Ball:

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        x = self.screen_width // 2
        y = self.screen_height // 2
        length = 10
        self.step = 10
        self.x_dir = self.step
        self.y_dir = self.step
        self.length = length
        self.collided = -1
        self.highest = 0
        self.prior = [
            pygame.Rect(x - 3 + n * self.step, y - 3 + n * self.step, 6, 6)
            for n in range(self.length-1)
        ]
        self.prior.append(
            pygame.Rect(x - 5 + self.length * self.step, y - 5 + self.length * self.step, 10, 10)
        )
        self.bloop_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "bloop.ogg"))

    def make_sound(self, frequency_l, frequency_r):
        sample_rate = 44100
        duration_in_samples = 44100
        max_sample = 2**9 - 1
        buf = numpy.zeros((duration_in_samples, 2), dtype=numpy.int16)
        for s in range(duration_in_samples):
            t = float(s) / sample_rate
            buf[s][0] = int(max_sample * math.sin(2.0 * math.pi * t * frequency_l))
            buf[s][1] = int(max_sample * math.sin(2.0 * math.pi * t * frequency_r))
        sound = pygame.sndarray.make_sound(buf)
        return sound

    def turn_left(self):
        self.x_dir = -self.step

    def turn_right(self):
        self.x_dir = self.step

    def turn_up(self):
        self.y_dir = -self.step

    def turn_down(self):
        self.y_dir = self.step

    def _check_collision(self) -> int:
        return self.prior[-1].collidelist(self.prior[0:-1])

    def move(self):
        head = self.prior[-1]
        move = head.move(self.x_dir, self.y_dir)
        redo = False
        if not 0 <= move.x + move.width//2 <= self.screen_width:
            self.x_dir = -self.x_dir
            redo = True
        if not 0 <= move.y + move.height//2 <= self.screen_height:
            self.y_dir = -self.y_dir
            redo = True
        if redo:
            move = head.move(self.x_dir, self.y_dir)
            self.bloop_sound.play().set_volume(1.0)
        head.update(head.x + 5 - 3, head.y + 5 - 3, 6, 6)
        self.prior.append(move)
        self.rect = move
        while len(self.prior) > self.length:
            self.prior.pop(0)
        self.collided = self._check_collision()
        self.length += 0.1
        self.highest = max(self.highest, int(self.length))
        if self.collided >= 0:
            self.length -= (self.collided + 1)

    def draw(self, screen):
        if self.collided >= 0:
            color = "red"
        else:
            color = "green"
        for prior in self.prior[0:-1]:
            pygame.draw.rect(screen, color, prior)
        prior = self.prior[-1]
        pygame.draw.rect(screen, color, prior)


class Bounce:
    """
    Let the snake bounce around the room.
    Don't let it eat its own tail.
    See how many segments you can accumulate.

    Left/Right/Up/Down Arrow Keys to change direction.

    +/- to change the speed
    """

    def __init__(self):
        self.speed = 10
        self.pause = 0.0
        self.screen_width = 640
        self.screen_height = 480

    async def run(self):
        await self.init()
        while await self.process_input():
            await self.update()
            await self.render()
        pygame.quit()

    async def init(self):
        pygame.init()
        self.ball = Ball(self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.munch_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "munch.ogg"))
        pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "music.ogg"))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)

    async def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_LEFT:
                    self.ball.turn_left()
                elif event.key == pygame.K_RIGHT:
                    self.ball.turn_right()
                elif event.key == pygame.K_UP:
                    self.ball.turn_up()
                elif event.key == pygame.K_DOWN:
                    self.ball.turn_down()
                elif event.key == pygame.K_EQUALS:
                    self.speed = min(90, self.speed + 1)
                elif event.key == pygame.K_MINUS:
                    self.speed = max(10, self.speed - 1)
        return True

    async def update(self):
        self.pause = max(0.0, self.pause - 0.1)
        if self.pause <= 0.0:
            self.ball.move()
        pygame.display.set_caption(f'Bounce (Speed {self.speed} , Length {int(self.ball.length)} , Highest {self.ball.highest})')
        self.screen.fill("purple")
        self.ball.draw(self.screen)
        self.speed = min(90, max(10, int(self.ball.length) // 3))

    async def render(self):
        pygame.display.flip()
        self.clock.tick(self.speed)
        await asyncio.sleep(0)
        if self.pause <= 0.0:
            if self.ball.collided >= 0:
                self.pause = self.speed / 10.0
                pygame.mixer.Sound.play(self.munch_sound).set_volume(1.0)


async def main():
    await Bounce().run()


def run():
    asyncio.run(main())


if __name__ == '__main__':
    run()
