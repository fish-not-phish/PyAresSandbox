from projectile import *
import pygame
import random
from lightning_laser import LightningLaser 
from utils import find_closest_enemy

class Weapon:
    def __init__(self, damage, fire_rate, projectile_type, sprite_sheet=None, pn_file=None, speed=10, lifetime=2, is_special=False, size=1.0, mass=0.0, sound_manager=None, fire_sound=None, hit_sound=None, explosion_type='weapon_hit', laser_color=(255, 0, 0), laser_length=100, laser_width=5, alternate_fire=False, alternate_offsets=None, turret=False, turret_projectiles=1, turret_spread=15,):
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

        # Alternation properties
        self.alternate_fire = alternate_fire
        if alternate_offsets is None:
            self.alternate_offsets = []
        else:
            self.alternate_offsets = alternate_offsets
        self.current_offset_idx = 0 

        # Turret properties
        self.turret = turret
        self.turret_projectiles = turret_projectiles
        self.turret_spread = turret_spread

    def fire(self, position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships, ship=None):
        if ship:
            self.ship = ship
        if self.cooldown <= 0:
            if self.alternate_fire and self.alternate_offsets:
                offset_vector = self.alternate_offsets[self.current_offset_idx]
                adjusted_position = position + offset_vector.rotate(angle)
                self.current_offset_idx = (self.current_offset_idx + 1) % len(self.alternate_offsets)
            else:
                adjusted_position = position

            if self.turret:
                if self.turret_projectiles > 1:
                    # Fire multiple projectiles with spread
                    total_spread = self.turret_spread
                    num_projectiles = self.turret_projectiles
                    start_angle = angle - (total_spread / 2)
                    angle_increment = total_spread / (num_projectiles - 1) if num_projectiles > 1 else 0

                    for i in range(num_projectiles):
                        current_angle = start_angle + (i * angle_increment)
                        self._create_projectile(adjusted_position, current_angle, projectiles, ship_velocity, origin_race, origin_relationship, ships)
                else:
                    # Turret enabled but single projectile
                    self._create_projectile(adjusted_position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships)
            else:
                self._create_projectile(adjusted_position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships)

            # Play weapon fire sound
            if self.sound_manager and self.fire_sound:
                self.sound_manager.play_sound(self.fire_sound)

            # Set cooldown
            self.cooldown = self.fire_rate

    def _create_projectile(self, position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships):
        # Create projectile based on type
        if self.projectile_type == 'tspace':
            # Find the closest enemy
            closest_enemy = find_closest_enemy(self.ship, ships)
            if closest_enemy:
                direction = closest_enemy.position - self.ship.position
                distance = direction.length()
                firing_angle = pygame.math.Vector2(0, -1).angle_to(direction)
                target_position = closest_enemy.position
            else:
                # No enemies; fire straight ahead with default length
                firing_angle = angle
                distance = self.laser_length  # Use default length
                target_position = None
            # Calculate total velocity (optional, based on game mechanics)
            firing_direction = pygame.math.Vector2(0, -1).rotate(firing_angle).normalize()
            total_velocity = firing_direction * self.speed + ship_velocity

            # Create LightningLaser with dynamic length
            laser = LightningLaser(
                offset_angle=firing_angle,
                distance=35,  # Distance from the ship
                laser_angle=firing_angle,
                length=distance if closest_enemy else self.laser_length,  # Dynamic length
                width=self.laser_width,
                color=self.laser_color,
                damage=self.damage,
                lifetime=self.lifetime,
                ship=self.ship,
                origin_race=origin_race,
                origin_relationship=origin_relationship
            )
            projectiles.add(laser)

        elif self.projectile_type == 'laser':
            # Calculate total velocity (ship's velocity + laser's speed)
            firing_direction = pygame.math.Vector2(0, -1).rotate(angle).normalize()
            total_velocity = firing_direction * self.speed + ship_velocity

            laser = Laser(
                position=position,
                angle=angle,
                color=self.laser_color,
                length=self.laser_length,
                width=self.laser_width,
                damage=self.damage,
                velocity=total_velocity.length(),
                lifetime=self.lifetime,
                size_scale=self.projectile_size,
                origin_race=origin_race,
                hit_sound=self.hit_sound,
                explosion_type=self.explosion_type,
                origin_relationship=origin_relationship,
            )
            projectiles.add(laser)

        elif self.projectile_type in ['cm', 'amissile', 'atomic', 'magno']:
            if self.projectile_type in ['atomic', 'magno']:
                max_rotation = 1.4
            else:
                max_rotation=0.6
            # Create a HomingMissile
            firing_direction = pygame.math.Vector2(0, -1).rotate(angle).normalize()
            total_velocity = firing_direction * self.speed + ship_velocity

            missile = HomingMissile(
                position=position,
                angle=angle,
                sprite_sheet=self.sprite_sheet,
                frames=self.frames,
                projectile_type=self.projectile_type,
                damage=self.damage,
                velocity=total_velocity,
                lifetime=self.lifetime,
                size=self.projectile_size,
                mass=self.mass,
                origin_race=origin_race,
                hit_sound=self.hit_sound,
                explosion_type=self.explosion_type,
                max_rotation=max_rotation,
                origin_relationship=origin_relationship,
            )
            projectiles.add(missile)

        else:
            # Regular Projectile
            if self.frames is None:
                print(f"Error: Weapon '{self.projectile_type}' has no frames loaded.")
                return

            firing_direction = pygame.math.Vector2(0, -1).rotate(angle).normalize()
            total_velocity = firing_direction * self.speed + ship_velocity

            projectile = Projectile(
                position=position,
                angle=angle,
                sprite_sheet=self.sprite_sheet,
                frames=self.frames,
                projectile_type=self.projectile_type,
                damage=self.damage,
                velocity=total_velocity,
                lifetime=self.lifetime,
                size=self.projectile_size,
                mass=self.mass,
                origin_race=origin_race,
                hit_sound=self.hit_sound,
                explosion_type=self.explosion_type,
                origin_relationship=origin_relationship,
            )
            projectiles.add(projectile)

    def update_cooldown(self, delta_time):
        if self.cooldown > 0:
            self.cooldown -= delta_time

    def update(self, delta_time, ship, ships, projectiles):
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
        self.origin_race = None
        self.origin_relationship = None

    def fire(self, position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships, ship=None):
        super().fire(position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships, ship=ship)
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

    def update(self, delta_time, ship, ships, projectiles):
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
            origin_race=ship.race,
            origin_relationship=ship.relationship,
        )
        self.attached_lasers.add(attached_laser)

    def draw(self, surface, camera, ship):
        for laser in self.attached_lasers:
            laser.draw(surface, camera)

class TSpaceWeapon(Weapon):
    def __init__(self, particles_group, **kwargs):
        super().__init__(**kwargs)
        self.particles_group = particles_group
        self.attached_lasers = pygame.sprite.Group()
        self.max_lasers = 1  # Only one laser allowed
        self.is_firing = False
        self.laser_timer = 0
        self.next_laser_time = random.uniform(0.5, 1.0)
        self.sound_timer = 0
        self.sound_interval = 0.5
        self.origin_race = None
        self.origin_relationship = None

    def fire(self, position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships, ship=None):
        super().fire(position, angle, projectiles, ship_velocity, origin_race, origin_relationship, ships, ship=ship)
        self.is_firing = True  # Start firing state
        if len(self.attached_lasers) == 0:
            # Find the closest enemy
            closest_enemy = find_closest_enemy(self.ship, ships)
            if closest_enemy:
                direction = closest_enemy.position - self.ship.position
                distance = direction.length()
                firing_angle = pygame.math.Vector2(0, -1).angle_to(direction)
                target_pos = closest_enemy.position
            else:
                # No enemies; fire straight ahead with default length
                firing_angle = self.ship.angle
                distance = self.laser_length  # Use default length
                target_pos = None

            # Create a single LightningLaser aimed towards firing_angle with dynamic length
            laser = LightningLaser(
                offset_angle=firing_angle,
                distance=distance / 2 if closest_enemy else self.laser_length / 2,  # Distance from the ship
                laser_angle=firing_angle,
                length=distance if closest_enemy else self.laser_length,  # Dynamic length
                width=self.laser_width,
                color=self.laser_color,
                damage=self.damage,
                lifetime=self.lifetime,
                ship=self.ship,
                origin_race=self.origin_race,
                origin_relationship=self.origin_relationship
            )
            self.attached_lasers.add(laser)
            # Play weapon fire sound
            if self.sound_manager and self.fire_sound:
                self.sound_manager.play_sound(self.fire_sound)

    def stop_firing(self):
        self.is_firing = False
        self.laser_timer = 0
        self.next_laser_time = random.uniform(0.5, 1.0)  # Reset interval

    def update(self, delta_time, ship, ships, projectiles):
        self.ship = ship  # Keep a reference to the ship
        self.sound_timer += delta_time  # Update the sound timer

        # Update attached lasers
        self.attached_lasers.update(delta_time)

        if self.is_firing:
            self.laser_timer += delta_time
            if self.laser_timer >= self.next_laser_time:
                self.laser_timer = 0
                self.next_laser_time = random.uniform(0.5, 1.0)
                # Add a new laser if under max limit
                if len(self.attached_lasers) < self.max_lasers:
                    closest_enemy = find_closest_enemy(self.ship, ships)
                    if closest_enemy:
                        direction = closest_enemy.position - self.ship.position
                        distance = direction.length()
                        firing_angle = pygame.math.Vector2(0, -1).angle_to(direction)
                        target_pos = closest_enemy.position
                    else:
                        firing_angle = self.ship.angle
                        distance = self.laser_length
                        target_pos = None

                    # Create a new LightningLaser with dynamic length
                    laser = LightningLaser(
                        offset_angle=firing_angle,
                        distance=35,  # Distance from the ship
                        laser_angle=firing_angle,
                        length=distance if closest_enemy else self.laser_length,
                        width=self.laser_width,
                        color=self.laser_color,
                        damage=self.damage,
                        lifetime=self.lifetime,
                        ship=self.ship,
                        origin_race=self.origin_race,
                        origin_relationship=self.origin_relationship
                    )
                    self.attached_lasers.add(laser)

                # Play weapon fire sound if enough time has passed
                if self.sound_manager and self.fire_sound and self.sound_timer >= self.sound_interval:
                    self.sound_manager.play_sound(self.fire_sound)
                    self.sound_timer = 0  # Reset sound timer
        else:
            # Not firing; do not add new lasers
            pass

    def draw(self, surface, camera, ship):
        for laser in self.attached_lasers:
            laser.draw(surface, camera)
