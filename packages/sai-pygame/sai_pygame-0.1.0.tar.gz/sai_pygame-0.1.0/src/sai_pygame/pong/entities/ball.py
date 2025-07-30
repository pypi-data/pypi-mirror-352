import pygame
from random import randint

BLACK = (0, 0, 0)


class Ball(pygame.sprite.Sprite):
    def __init__(self, color, diameter, screen_width, screen_height, max_speed=7):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.diameter = diameter

        self.max_speed = max_speed

        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        pygame.draw.rect(self.image, color, [0, 0, self.diameter, self.diameter])

        self.rect = self.image.get_rect()

        self.reset()

    def reset(self):
        self.velocity: list[float] = [
            randint(3, self.max_speed),
            randint(-self.max_speed, self.max_speed),
        ]
        self.rect.x = self.diameter * 2
        self.rect.y = self.diameter * 2

    def update(self):
        self.rect.x += int(self.velocity[0])
        self.rect.y += int(self.velocity[1])

    def bounce(self, paddleAction=None):
        self.velocity[0] = -self.velocity[0]
        if paddleAction == "down":
            self.velocity[1] = min(
                self.velocity[1] + self.max_speed / 10, self.max_speed
            )
        elif paddleAction == "up":
            self.velocity[1] = max(
                self.velocity[1] - self.max_speed / 10, -self.max_speed
            )
        else:
            self.velocity[1] = randint(-2, 2)
