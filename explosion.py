# explosion.py

import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, position, sprite_sheet, frames, size=1.0, duration=0.5, animation_speed=1.0):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.sprite_sheet = sprite_sheet
        self.frames = frames
        self.size_scale = size
        self.duration = duration  # Total duration of the explosion animation
        self.elapsed_time = 0
        self.animation_speed = animation_speed  # Add this line
        self.frame_duration = (self.duration / len(self.frames)) * (1 / self.animation_speed)
        self.current_frame = 0
        self.image = None
        self.rect = None
        self.load_image()

    def load_image(self):
        frame = self.frames[self.current_frame]
        sprite_rect = pygame.Rect(
            frame['left'], frame['top'],
            frame['right'] - frame['left'], frame['bottom'] - frame['top']
        )
        original_image = self.sprite_sheet.subsurface(sprite_rect).copy()
        scaled_width = int(sprite_rect.width * self.size_scale)
        scaled_height = int(sprite_rect.height * self.size_scale)
        self.image = pygame.transform.smoothscale(
            original_image, (scaled_width, scaled_height)
        )
        self.rect = self.image.get_rect(center=self.position)

    def update(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.kill()
            return

        # Update frame based on elapsed time
        frame_number = int(self.elapsed_time / self.frame_duration)
        if frame_number != self.current_frame and frame_number < len(self.frames):
            self.current_frame = frame_number
            self.load_image()

    def draw(self, surface, camera):
        # Convert world position to screen position
        screen_position = camera.world_to_screen(self.position)
        scaled_image = pygame.transform.smoothscale(
            self.image,
            (
                int(self.rect.width * camera.zoom_level),
                int(self.rect.height * camera.zoom_level),
            )
        )
        scaled_rect = scaled_image.get_rect(
            center=(int(screen_position.x), int(screen_position.y))
        )
        surface.blit(scaled_image, scaled_rect.topleft)
