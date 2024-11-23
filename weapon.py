from projectile import *
import pygame
import random
from utils import spawn_particles

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

    def update(self, delta_time, ship):
        # Default implementation does nothing
        pass

    def draw(self, surface, camera, ship):
        # Default implementation does nothing
        pass

class TrazerWeapon(Weapon):
    def __init__(self, particles_group, **kwargs):
        super().__init__(**kwargs)
        self.particles_group = particles_group
        self.attached_lasers = pygame.sprite.Group()
        self.laser_timer = 0
        self.next_laser_time = random.uniform(0.5, 1.0)
        self.max_lasers = 12
        self.is_firing = False
        self.sound_timer = 0
        self.sound_interval = 0.5

    def fire(self, position, angle, projectiles, ship_velocity, origin_race):
        self.is_firing = True  # Start firing state
        if len(self.attached_lasers) == 0:
            # On first fire, add multiple lasers
            self.add_initial_lasers(self.ship)
            # Play weapon fire sound
            if self.sound_manager and self.fire_sound:
                self.sound_manager.play_sound(self.fire_sound)

    def stop_firing(self):
        self.is_firing = False
        # Do not clear attached_lasers; let them expire naturally
        self.laser_timer = 0
        self.next_laser_time = random.uniform(0.5, 1.0)  # Keep interval consistent

    def update(self, delta_time, ship):
        self.ship = ship  # Keep a reference to the ship
        self.sound_timer += delta_time  # Update the sound timer

        # Update attached lasers regardless of firing state
        self.attached_lasers.update(delta_time)

        if self.is_firing:
            self.laser_timer += delta_time
            if self.laser_timer >= self.next_laser_time:
                self.laser_timer = 0
                self.next_laser_time = random.uniform(0.5, 1.0)
                # Add multiple lasers at each interval
                lasers_to_add = random.randint(1, 3)  # Spawn 1 to 3 lasers
                for _ in range(lasers_to_add):
                    if len(self.attached_lasers) < self.max_lasers:
                        self.add_new_laser(ship)
                # Play weapon fire sound if enough time has passed
                if self.sound_manager and self.fire_sound and self.sound_timer >= self.sound_interval:
                    self.sound_manager.play_sound(self.fire_sound)
                    self.sound_timer = 0  # Reset sound timer
        else:
            # Not firing; do not add new lasers
            pass

    def add_initial_lasers(self, ship):
        initial_lasers_to_add = 3  # Spawn 3 lasers when starting to fire
        for _ in range(initial_lasers_to_add):
            if len(self.attached_lasers) < self.max_lasers:
                self.add_new_laser(ship)

    def add_new_laser(self, ship):
        # Generate a random angle between 0 and 360 degrees
        laser_angle = random.uniform(0, 360)
        radius = 35  # Adjust as needed
        distance = radius

        # Random lifetime and length
        lifetime = random.uniform(1, 2)
        min_length = 50
        max_length = 100
        laser_length = random.uniform(min_length, max_length)

        attached_laser = AttachedLaser(
            offset_angle=laser_angle,  # World angle
            distance=distance,
            laser_angle=laser_angle,   # World angle
            length=laser_length,
            width=self.laser_width,
            color=self.laser_color,
            damage=self.damage,
            lifetime=lifetime,
            ship=ship,
            origin_race=ship.race
        )
        self.attached_lasers.add(attached_laser)

    def draw(self, surface, camera, ship):
        for laser in self.attached_lasers:
            laser.draw(surface, camera)
