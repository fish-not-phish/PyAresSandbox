import pygame

class Particle(pygame.sprite.Sprite):
    def __init__(self, position, velocity, lifetime, color):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(velocity)
        self.lifetime = lifetime
        self.elapsed_time = 0
        self.color = color

        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.lifetime:
            self.kill()
            return

        # Update position
        self.position += self.velocity
        self.rect.center = self.position

        # Optional: Fade out over time
        fade_factor = 1 - (self.elapsed_time / self.lifetime)
        faded_color = (
            int(self.color[0] * fade_factor),
            int(self.color[1] * fade_factor),
            int(self.color[2] * fade_factor),
        )
        self.image.fill(faded_color)

    def draw(self, surface, camera):
        screen_position = camera.world_to_screen(self.position)
        surface.blit(self.image, (screen_position.x, screen_position.y))
