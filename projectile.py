import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, angle, sprite_sheet, frames, projectile_type, damage, velocity, lifetime, size=1.0, mass=0.0, origin_race=None, hit_sound=None, explosion_type='weapon_hit'):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.velocity = velocity  # Use the velocity passed in
        self.angle = angle
        self.sprite_sheet = sprite_sheet
        self.frames = frames
        self.projectile_type = projectile_type
        self.damage = damage
        self.lifetime = lifetime  # Lifetime in seconds
        self.elapsed_time = 0  # Track how long the projectile has existed
        self.image_idx = 0
        self.animation_speed = 0.1
        self.frame_timer = 0
        self.zoom_level = 1.0
        self.shape_render_threshold = 0.3
        self.shape_size = 5
        self.size_scale = size
        self.mass = mass
        self.origin_race = origin_race
        self.hit_sound = hit_sound
        self.explosion_type = explosion_type
        self.load_image()

    def set_zoom_level(self, zoom_level):
        """Set the current zoom level for the projectile and adjust shape size."""
        self.zoom_level = zoom_level
        self.shape_size = max(2, int(10 * self.zoom_level))  # Shape size adjusts with zoom
        self.load_image()

    def load_image(self):
        """Load and scale the projectile image based on the current zoom level."""
        if self.zoom_level < self.shape_render_threshold:
            # If rendering as a shape, don't update the image
            return

        if self.projectile_type == "missile":
            # Use the first frame for missiles
            frame = self.frames[0]
        else:
            # Cycle through frames for animated projectiles
            frame = self.frames[self.image_idx]

        # Extract the frame from the sprite sheet
        sprite_rect = pygame.Rect(frame['left'], frame['top'], frame['right'] - frame['left'], frame['bottom'] - frame['top'])
        original_image = self.sprite_sheet.subsurface(sprite_rect).copy()

        # Scale the sprite image based on the zoom level
        original_width = sprite_rect.width
        original_height = sprite_rect.height
        scaled_width = int(original_width * self.size_scale)
        scaled_height = int(original_height * self.size_scale)
        self.image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))

        # Rotate the image to match the projectile's angle
        self.image = pygame.transform.rotate(self.image, -self.angle)

        # Update the rect for positioning
        self.rect = self.image.get_rect(center=self.position)

    def update(self, delta_time):
        """Update the projectile's position and lifetime."""
        # Update the elapsed time
        self.elapsed_time += delta_time
        if self.elapsed_time > self.lifetime:
            self.kill()  # Remove the projectile if it exceeds its lifetime
            return  # Exit early since the projectile is no longer active

        # Update position
        self.position += self.velocity * delta_time
        self.rect.center = self.position

        # Handle animation if applicable
        if self.projectile_type != "missile" and self.zoom_level >= self.shape_render_threshold:
            self.frame_timer += delta_time
            if self.frame_timer >= self.animation_speed:
                self.image_idx = (self.image_idx + 1) % len(self.frames)
                self.load_image()
                self.frame_timer = 0

    def draw(self, surface, camera):
        # Convert world position to screen position
        screen_position = camera.world_to_screen(self.position)

        if camera.zoom_level < 0.3:  # Render as a shape when zoomed out far enough
            size = max(2, int(10 * camera.zoom_level * self.size_scale))  # Base size of the square
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                pygame.Rect(
                    int(screen_position.x - size / 2),
                    int(screen_position.y - size / 2),
                    size,
                    size
                )
            )
        else:
            # Scale the sprite based on the camera's zoom level
            scaled_image = pygame.transform.smoothscale(
                self.image,
                (
                    int(self.rect.width * camera.zoom_level),
                    int(self.rect.height * camera.zoom_level),
                )
            )

            # Create a new rect for the scaled image
            scaled_rect = scaled_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))

            # Blit the scaled image to the surface
            surface.blit(scaled_image, scaled_rect.topleft)

class Laser(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        angle,
        color,
        length,
        width,
        damage,
        velocity,
        lifetime,
        size_scale=1.0,  # Add this parameter with a default value
        origin_race=None,
        hit_sound=None,
        explosion_type='weapon_hit'
    ):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, -1).rotate(angle) * velocity
        self.angle = angle
        self.color = color  # RGB color tuple
        self.length = length  # Base length of the laser
        self.width = width  # Base width of the laser
        self.damage = damage  # Damage the laser deals
        self.lifetime = lifetime  # Duration the laser exists in seconds
        self.elapsed_time = 0  # Time the laser has been active
        self.origin_race = origin_race
        self.hit_sound = hit_sound
        self.explosion_type = explosion_type
        self.size_scale = size_scale  # Add this line to store the size scale

        # Calculate the rectangle representing the laser
        self.load_image()

    def load_image(self):
        # Adjust length and width based on size_scale
        adjusted_length = self.length * self.size_scale
        adjusted_width = self.width * self.size_scale

        # Create a surface for the laser rectangle
        self.image = pygame.Surface((adjusted_width, adjusted_length), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, adjusted_width, adjusted_length))

        # Rotate the image to match the firing angle
        self.image = pygame.transform.rotate(self.image, -self.angle)

        # Update the rect for positioning
        self.rect = self.image.get_rect(center=self.position)

        # Create a mask for pixel-perfect collision detection
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        """Update the laser's position and lifetime."""
        # Update the elapsed time and kill the laser if it exceeds its lifetime
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.lifetime:
            self.kill()
            return

        # Update position based on velocity
        self.position += self.velocity * delta_time
        self.rect.center = self.position

    def draw(self, surface, camera):
        """Draw the laser."""
        screen_position = camera.world_to_screen(self.position)

        # Scale the image based on the camera's zoom level
        scaled_image = pygame.transform.smoothscale(
            self.image,
            (
                int(self.rect.width * camera.zoom_level),
                int(self.rect.height * camera.zoom_level),
            )
        )
        scaled_rect = scaled_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))

        # Blit the scaled image to the surface
        surface.blit(scaled_image, scaled_rect.topleft)

class AttachedLaser(pygame.sprite.Sprite):
    def __init__(self, offset_angle, distance, laser_angle, length, width, color, damage, lifetime, ship, origin_race):
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
        self.particle_spawn_cooldown = 0.0

        # Calculate initial offset vector without ship's angle
        self.initial_offset = pygame.math.Vector2(0, -self.distance).rotate(self.offset_angle)
        # Store the laser's initial angle (world angle)
        self.laser_angle = laser_angle  # Already set

        # Create a surface for collision detection
        self.image = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.length))
        self.original_image = self.image.copy()

        self.update_position()


    def get_start_position(self):
        """Calculate the start position of the laser."""
        # The start position is where the laser leaves the ship
        offset = pygame.math.Vector2(0, -self.distance).rotate(self.ship.angle + self.offset_angle)
        start_position = self.ship.position + offset
        return start_position

    def update_position(self):
        # Update the laser's position without considering the ship's rotation
        self.position = self.ship.position + self.initial_offset

        # Rotate the image only by the laser's own angle (constant)
        self.image = pygame.transform.rotate(self.original_image, -self.laser_angle)
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.lifetime:
            self.kill()
            return

        # Update position and rotation
        self.update_position()

        # Update particle spawn cooldown
        if self.particle_spawn_cooldown > 0:
            self.particle_spawn_cooldown -= delta_time

    def draw(self, surface, camera):
        # Update position and rotation before drawing
        self.update_position()

        # Draw the laser
        screen_position = camera.world_to_screen(self.position)

        # Scale the image based on the camera's zoom level
        scaled_image = pygame.transform.smoothscale(
            self.image,
            (
                int(self.rect.width * camera.zoom_level),
                int(self.rect.height * camera.zoom_level),
            )
        )
        scaled_rect = scaled_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))

        # Blit the scaled image to the surface
        surface.blit(scaled_image, scaled_rect.topleft)

# projectile.py

class HomingMissile(Projectile):
    def __init__(self, position, angle, sprite_sheet, frames, projectile_type, damage, velocity, lifetime, size=1.0, mass=0.0, origin_race=None, hit_sound=None, explosion_type='weapon_hit', max_rotation=5):
        super().__init__(position, angle, sprite_sheet, frames, projectile_type, damage, velocity, lifetime, size, mass, origin_race, hit_sound, explosion_type)
        self.is_homing = True
        self.max_rotation = max_rotation  # Degrees per frame, adjust as needed

    def update(self, delta_time, ships):
        """Update the missile's position and apply homing behavior."""
        # Update the elapsed time
        self.elapsed_time += delta_time
        if self.elapsed_time > self.lifetime:
            self.kill()
            return

        # Homing behavior
        if self.is_homing:
            # Find the closest enemy ship
            min_distance = float('inf')
            closest_ship = None
            for ship in ships:
                if ship.race != self.origin_race:
                    distance = self.position.distance_to(ship.position)
                    if distance < min_distance:
                        min_distance = distance
                        closest_ship = ship
            if closest_ship:
                # Calculate the desired direction
                desired_direction = (closest_ship.position - self.position).normalize()
                # Calculate the current velocity direction
                current_direction = self.velocity.normalize()
                # Calculate the angle between current velocity and desired direction
                angle_between = current_direction.angle_to(desired_direction)
                # Limit the rotation angle per frame
                rotation_angle = min(abs(angle_between), self.max_rotation)
                # Restore the sign of the angle
                if angle_between < 0:
                    rotation_angle = -rotation_angle
                # Rotate the velocity vector
                self.velocity = self.velocity.rotate(rotation_angle)
                # Update the angle for rendering
                self.angle = -self.velocity.angle_to(pygame.math.Vector2(0, -1))
        
        # Update position
        self.position += self.velocity * delta_time
        self.rect.center = self.position

        # For missiles, use only the first frame; no animation needed
        self.load_image()

    def load_image(self):
        """Load and rotate the missile image based on current angle."""
        # Use the first frame for missiles
        frame = self.frames[0]

        # Extract the frame from the sprite sheet
        sprite_rect = pygame.Rect(frame['left'], frame['top'], frame['right'] - frame['left'], frame['bottom'] - frame['top'])
        original_image = self.sprite_sheet.subsurface(sprite_rect).copy()

        # Scale the sprite image based on the size scale
        original_width = sprite_rect.width
        original_height = sprite_rect.height
        scaled_width = int(original_width * self.size_scale)
        scaled_height = int(original_height * self.size_scale)
        self.image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))

        # Rotate the image to match the missile's angle
        self.image = pygame.transform.rotate(self.image, -self.angle)

        # Update the rect for positioning
        self.rect = self.image.get_rect(center=self.position)

        # Create a mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
