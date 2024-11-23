from projectile import Projectile, Laser
import pygame

class Weapon:
    def __init__(self, damage, fire_rate, projectile_type, sprite_sheet=None, pn_file=None, speed=10, lifetime=2, is_special=False, size=1.0, mass=0.0, sound_manager=None, fire_sound=None, hit_sound=None, explosion_type='weapon_hit', laser_color=(255, 0, 0), laser_length=100, laser_width=5):
        self.damage = damage
        self.fire_rate = fire_rate
        self.projectile_type = projectile_type
        self.sprite_sheet = sprite_sheet
        self.frames = pn_file
        self.speed = speed  # Projectile speed
        self.lifetime = lifetime  # Projectile lifetime in seconds
        self.is_special = is_special
        self.cooldown = 0
        self.projectile_size = size  # For projectiles
        self.mass = mass
        self.sound_manager = sound_manager
        self.fire_sound = fire_sound
        self.hit_sound = hit_sound
        self.explosion_type = explosion_type

        # Laser-specific properties
        self.laser_color = laser_color
        self.laser_length = laser_length
        self.laser_width = laser_width

    def fire(self, position, angle, projectiles, ship_velocity, origin_race):
        if self.cooldown <= 0:
            if self.projectile_type == 'laser':
                # Calculate total velocity (ship's velocity + laser's speed)
                firing_direction = pygame.math.Vector2(0, -1).rotate(angle).normalize()
                total_velocity = firing_direction * self.speed + ship_velocity

                laser = Laser(
                    position=position,
                    angle=angle,
                    color=self.laser_color,
                    length=self.laser_length,     # Base length
                    width=self.laser_width,       # Base width
                    damage=self.damage,
                    velocity=total_velocity.length(),  # Speed magnitude
                    lifetime=self.lifetime,
                    size_scale=self.projectile_size,   # Pass size_scale here
                    origin_race=origin_race,
                    hit_sound=self.hit_sound,
                    explosion_type=self.explosion_type
                )
                projectiles.add(laser)
            else:
                # Logic for other projectiles
                firing_direction = pygame.math.Vector2(0, -1).rotate(angle).normalize()
                total_velocity = firing_direction * self.speed + ship_velocity
                projectile = Projectile(
                    position,
                    angle,
                    self.sprite_sheet,
                    self.frames,
                    self.projectile_type,
                    self.damage,
                    total_velocity,
                    self.lifetime,
                    size=self.projectile_size,
                    mass=self.mass,
                    origin_race=origin_race,
                    hit_sound=self.hit_sound,
                    explosion_type=self.explosion_type,
                )
                projectiles.add(projectile)

            # Play weapon fire sound
            if self.sound_manager and self.fire_sound:
                self.sound_manager.play_sound(self.fire_sound)

            # Set cooldown
            self.cooldown = self.fire_rate

    def update_cooldown(self, delta_time):
        if self.cooldown > 0:
            self.cooldown -= delta_time
