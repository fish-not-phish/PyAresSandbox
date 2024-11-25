# lightning_laser.py
import pygame
import random

class LightningLaser(pygame.sprite.Sprite):
    def __init__(
        self,
        offset_angle,
        distance,
        laser_angle,
        length,
        width,
        color=(255, 255, 0),  # Yellow color
        damage=10,
        lifetime=2,
        ship=None,
        origin_race=None,
        origin_relationship=None,
        animation_speed=300  # Increased speed for more dynamic movement
    ):
        super().__init__()
        self.offset_angle = offset_angle
        self.distance = distance
        self.laser_angle = laser_angle
        self.length = length
        self.width = width
        self.color = color
        self.damage = damage
        self.lifetime = lifetime
        self.elapsed_time = 0
        self.ship = ship
        self.origin_race = origin_race
        self.origin_relationship = origin_relationship

        # Calculate initial offset vector based on the ship's angle
        self.initial_offset = pygame.math.Vector2(0, -self.distance).rotate(self.laser_angle)

        # Initialize animation variables
        self.animation_phase = 0  # Tracks the animation phase
        self.animation_speed = animation_speed  # Controls the speed of animation

        # Generate the initial zig-zag pattern
        self.image = self.generate_zig_zag_image(self.animation_phase)
        self.original_image = self.image.copy()

        # Set the initial position and angle
        self.update_position()

    def generate_zig_zag_image(self, phase=0):
        """
        Generates a surface with a moving zig-zag (lightning-like) pattern.
        The 'phase' parameter allows the zig-zag to shift horizontally for animation.
        """
        zigzag_width = self.width * 4  # Increased amplitude for larger zig-zags
        zigzag_length = self.length
        surface = pygame.Surface((zigzag_width, zigzag_length), pygame.SRCALPHA)
        surface = surface.convert_alpha()

        # Parameters for the zig-zag
        num_zigs = 30  # Increased number of zig-zags for a more chaotic pattern
        zigzag_height = zigzag_length / num_zigs
        zigzag_amplitude = self.width * 4  # Increased amplitude for more violent zig-zags

        points = []
        for i in range(num_zigs + 1):
            y = i * zigzag_height
            # Alternate the x position based on phase to animate
            if (i + phase) % 2 == 0:
                x = 0
            else:
                x = zigzag_amplitude
            points.append((x, y))

        # Draw the zig-zag line
        pygame.draw.lines(surface, self.color, False, points, self.width)

        return surface

    def update_position(self, target_position=None):
        """
        Updates the laser's position and orientation based on the ship's position.
        """
        if target_position:
            # Calculate the angle towards the target
            direction = target_position - self.ship.position
            self.laser_angle = pygame.math.Vector2(0, -1).angle_to(direction)
            self.initial_offset = pygame.math.Vector2(0, -self.distance).rotate(self.laser_angle)

        # Update position based on the ship's current position
        self.position = self.ship.position + self.initial_offset

        # Rotate the image to match the laser's angle
        self.image = pygame.transform.rotate(self.original_image, -self.laser_angle)
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time, target_position=None):
        """
        Updates the laser's position, animation, angle, and lifetime.
        """
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.lifetime:
            self.kill()
            return

        # Update the angle if a new target position is provided
        if target_position:
            self.update_position(target_position)

        # Update animation phase for horizontal movement
        self.animation_phase += self.animation_speed * delta_time
        self.animation_phase %= 2  # Loop between 0 and 2 for phase shift

        # Regenerate the zig-zag image with the updated phase
        self.image = self.generate_zig_zag_image(int(self.animation_phase))
        self.original_image = self.image.copy()

        # Update position and rotation after animation
        self.update_position(target_position)

    def draw(self, surface, camera):
        """
        Draws the laser on the given surface using the camera's transformation.
        """
        screen_position = camera.world_to_screen(self.position)

        # Scale the image based on the camera's zoom level
        scaled_image = pygame.transform.smoothscale(
            self.image,
            (
                max(1, int(self.rect.width * camera.zoom_level)),
                max(1, int(self.rect.height * camera.zoom_level)),
            )
        )

        scaled_rect = scaled_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))

        # Blit the scaled image to the surface
        surface.blit(scaled_image, scaled_rect.topleft)
