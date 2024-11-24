from ship import Ship
from level import Level
from grid import draw_grid
from utils import load_ship_assets, load_explosion_assets
import pygame
from pygame.locals import *
import sys
from camera import Camera
from sound_manager import SoundManager
import os
from explosion import Explosion
from projectile import *
from weapon import *
from particle import Particle
import random

# Particle group
particles = pygame.sprite.Group()

def find_closest_enemy(ship, ships):
    min_distance = float('inf')
    closest_ship = None
    for other_ship in ships:
        if other_ship != ship and other_ship.relationship != ship.relationship:
            distance = ship.position.distance_to(other_ship.position)
            if distance < min_distance:
                min_distance = distance
                closest_ship = other_ship
    return closest_ship

def handle_attached_laser_collision(ship, laser, collision_position):
    global delta_time
    # Check relationship before applying damage
    if ((laser.origin_relationship == 'friend' and ship.relationship == 'foe') or
        (laser.origin_relationship == 'foe' and ship.relationship == 'friend')):
        
        # Apply damage to the ship
        ship.health -= laser.damage * delta_time  # Damage over time

        # Spawn particles at the collision point if cooldown allows
        if laser.particle_spawn_cooldown <= 0:
            spawn_particles(collision_position)
            laser.particle_spawn_cooldown = 0.2

def spawn_particles(collision_position):
    # Spawn particles at the point of collision
    num_particles = random.randint(1, 2)  # Adjust as needed
    for _ in range(num_particles):
        particle = Particle(
            position=collision_position,
            velocity=pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2)),
            lifetime=random.uniform(0.5, 1.0),
            color=(random.randint(200, 255), random.randint(0, 50), random.randint(0, 50))
        )
        particles.add(particle)

def handle_projectile_collision(ship, projectile):
    # Check relationship before applying damage
    if ((projectile.origin_relationship == 'friend' and ship.relationship == 'foe') or
        (projectile.origin_relationship == 'foe' and ship.relationship == 'friend')):

        # Apply damage to the ship
        ship.health -= projectile.damage

        # Remove the projectile
        projectile.kill()

        # Play the projectile's hit sound
        if hasattr(projectile, 'hit_sound') and projectile.hit_sound:
            sound_manager.play_sound(projectile.hit_sound)

        # Select the appropriate explosion assets based on the projectile's explosion_type
        if hasattr(projectile, 'explosion_type'):
            if projectile.explosion_type == 'missile_hit':
                explosion_sprite_sheet = missile_hit_sprite_sheet
                explosion_frames = missile_hit_frames
                animation_speed = 1.0  
                duration = 1.0
            else:
                explosion_sprite_sheet = weapon_hit_sprite_sheet
                explosion_frames = weapon_hit_frames
                animation_speed = 1.0  
                duration = 0.3

        explosion = Explosion(
            position=projectile.position,
            sprite_sheet=explosion_sprite_sheet,
            frames=explosion_frames,
            size=projectile.size_scale,
            duration=duration,           
            animation_speed=animation_speed  
        )
        explosions.add(explosion)

def handle_ship_collision(ship1, ship2):
    # Calculate the normal vector between the ships
    collision_normal = ship2.position - ship1.position
    distance = collision_normal.length()
    if distance == 0:
        collision_normal = pygame.math.Vector2(1, 0)
        distance = 1  # Avoid division by zero
    else:
        collision_normal /= distance  # Normalize

    # Calculate overlap
    total_radius = (ship1.rect.width * ship1.size_scale) / 2 + (ship2.rect.width * ship2.size_scale) / 2
    overlap = total_radius - distance

    # Correct positions first
    if overlap > 0:
        total_inverse_mass = (1 / ship1.mass) + (1 / ship2.mass)
        if total_inverse_mass == 0:
            return
        correction_per_inverse_mass = collision_normal * (overlap / total_inverse_mass)
        ship1.position -= correction_per_inverse_mass * (1 / ship1.mass)
        ship2.position += correction_per_inverse_mass * (1 / ship2.mass)
        # Update the rects
        ship1.rect.center = ship1.position
        ship2.rect.center = ship2.position

    # Recalculate collision normal after position correction
    collision_normal = ship2.position - ship1.position
    distance = collision_normal.length()
    if distance != 0:
        collision_normal /= distance
    else:
        collision_normal = pygame.math.Vector2(1, 0)

    # Calculate relative velocity
    relative_velocity = ship1.velocity - ship2.velocity

    # Calculate relative velocity along the normal
    velocity_along_normal = relative_velocity.dot(collision_normal)

    # Do not resolve if velocities are separating
    if velocity_along_normal > 0:
        return

    # Coefficient of restitution
    restitution = 0.5

    # Calculate the impulse scalar
    impulse_scalar = -(1 + restitution) * velocity_along_normal
    impulse_scalar /= (1 / ship1.mass + 1 / ship2.mass)

    # Apply impulse to the ships
    impulse = impulse_scalar * collision_normal

    ship1.velocity += impulse / ship1.mass
    ship2.velocity -= impulse / ship2.mass

    # Optional: Apply damping to reduce sliding
    damping_factor = 0.98
    ship1.velocity *= damping_factor
    ship2.velocity *= damping_factor

def check_ship_collision(ship1, ship2):
    distance = ship1.position.distance_to(ship2.position)
    total_radius = (ship1.rect.width * ship1.size_scale) / 2 + (ship2.rect.width * ship2.size_scale) / 2
    return distance < total_radius

def check_projectile_collision(ship, projectile):
    # Using pixel-perfect collision detection
    if pygame.sprite.collide_mask(ship, projectile):
        return True
    return False

# Initialize pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init()

# Create an instance of SoundManager
sound_manager = SoundManager()

# Set up screen
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyAres")
clock = pygame.time.Clock()

# Base assets path
BASE_ASSETS_PATH = "assets"

# Load explosion assets
weapon_hit_sprite_sheet, weapon_hit_frames = load_explosion_assets(BASE_ASSETS_PATH, 'weapon_hit_explosion')
missile_hit_sprite_sheet, missile_hit_frames = load_explosion_assets(BASE_ASSETS_PATH, 'missile_hit_explosion')
ship_explosion_sprite_sheet, ship_explosion_frames = load_explosion_assets(BASE_ASSETS_PATH, 'ship_explosion')

# Load sounds
sound_manager.load_sound('onas_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'onas_fire.wav'))
sound_manager.load_sound('inasa_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'inasa_fire.wav'))
sound_manager.load_sound('asb_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'asb_fire.wav'))
sound_manager.load_sound('cform_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'cform_fire.wav'))
sound_manager.load_sound('amissile_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'amissile_fire.wav'))
sound_manager.load_sound('trazer_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'trazer_fire.wav'))
sound_manager.load_sound('anti_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'anti_fire.wav'))
sound_manager.load_sound('chronon_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'chronon_fire.wav'))
sound_manager.load_sound('cluster_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'cluster_fire.wav'))
sound_manager.load_sound('fireball_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'fireball_fire.wav'))
sound_manager.load_sound('fusion_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'fusion_fire.wav'))
sound_manager.load_sound('lepton_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'lepton_fire.wav'))
sound_manager.load_sound('magneto_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'magneto_fire.wav'))
sound_manager.load_sound('magno_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'magno_fire.wav'))
sound_manager.load_sound('neutron_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'neutron_fire.wav'))
sound_manager.load_sound('newo_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'newo_fire.wav'))
sound_manager.load_sound('gunshot_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'gunshot_fire.wav'))
sound_manager.load_sound('ish_laser_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'ish_laser_fire.wav'))
sound_manager.load_sound('sal_laser_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'sal_laser_fire.wav'))
sound_manager.load_sound('can_laser_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'can_laser_fire.wav'))
sound_manager.load_sound('uns_laser_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'uns_laser_fire.wav'))
sound_manager.load_sound('photo_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'photo_fire.wav'))
sound_manager.load_sound('pp_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'pp_fire.wav'))
sound_manager.load_sound('rplasma_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'rplasma_fire.wav'))
sound_manager.load_sound('ele_laser_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'ele_laser_fire.wav'))
sound_manager.load_sound('fusion_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'fusion_fire.wav'))
sound_manager.load_sound('missile_fire', os.path.join(BASE_ASSETS_PATH, 'sounds', 'missile_fire.wav'))
sound_manager.load_sound('basic_weapon_hit', os.path.join(BASE_ASSETS_PATH, 'sounds', 'basic_weapon_hit.wav'))
sound_manager.load_sound('missile_weapon_hit', os.path.join(BASE_ASSETS_PATH, 'sounds', 'missile_weapon_hit.wav'))
sound_manager.load_sound('explosion', os.path.join(BASE_ASSETS_PATH, 'sounds', 'explosion.wav'))

# Load level
current_level = Level(1)  # Load level 1

# Load ships for the level
ships = []
for ship_config in current_level.ships:
    race = ship_config["race"]
    ship_type = ship_config["type"]
    weapon_data = ship_config["weapons"]
    relationship = ship_config["relationship"]

    # Load ship assets
    sprite_sheet, frames = load_ship_assets(BASE_ASSETS_PATH, race, ship_type)

    # Use the position from the ship configuration
    x = ship_config.get("x", SCREEN_WIDTH // 2)
    y = ship_config.get("y", SCREEN_HEIGHT // 2)

    # Add sound_manager to ship_config
    ship_config["sound_manager"] = sound_manager

    # Create the ship
    ship = Ship(
        race=race,
        relationship=relationship,
        x=x,
        y=y,
        frames=frames,
        ship_sheet=sprite_sheet,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        config=ship_config,  # Pass the entire ship configuration
        particles_group=particles,
    )
    ships.append(ship)

# Projectile group
projectiles = pygame.sprite.Group()

# Explosion group
explosions = pygame.sprite.Group()

# Initialize the camera
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# Main game loop
running = True
while running:
    delta_time = clock.tick(60) / 1000.0  # Time elapsed since last frame

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Check for key presses
        elif event.type == KEYDOWN:
            if event.key == K_PLUS or event.key == K_EQUALS:
                camera.adjust_zoom(0.1)  # Zoom in
            elif event.key == K_MINUS:
                camera.adjust_zoom(-0.1)  # Zoom out

    # Continuous key presses for movement (only for player ship in this case)
    keys = pygame.key.get_pressed()
    if ships:  # Ensure there's at least one ship
        player_ship = ships[0]
        if keys[K_LEFT]:
            player_ship.rotate_left()
        if keys[K_RIGHT]:
            player_ship.rotate_right()
        if keys[K_UP]:
            player_ship.accelerate()
        if keys[K_DOWN]:
            player_ship.decelerate()
        weapon_slots = {
            "primary": K_SPACE,
            "secondary": K_LSHIFT,
            "special": K_c,
        }

        # Handle firing for each weapon slot
        for weapon_type, key in weapon_slots.items():
            if keys[key]:
                weapon = getattr(player_ship, f"{weapon_type}_weapon", None)
                if weapon:
                    if weapon.turret:
                        # Turret is enabled; aim towards the closest enemy
                        closest_enemy = find_closest_enemy(player_ship, ships)
                        if closest_enemy:
                            direction = closest_enemy.position - player_ship.position
                            firing_angle = pygame.math.Vector2(0, -1).angle_to(direction)
                        else:
                            # No enemies; fire straight ahead
                            firing_angle = player_ship.angle
                    else:
                        # Turret is disabled; always fire straight ahead
                        firing_angle = player_ship.angle
                    player_ship.fire_weapon(weapon_type, projectiles, firing_angle)
            else:
                # Stop firing if the key is not pressed and the weapon supports continuous firing
                weapon = getattr(player_ship, f"{weapon_type}_weapon", None)
                if isinstance(weapon, TrazerWeapon):
                    weapon.stop_firing()
        
    # Update camera position to follow the player ship
    if ships:
        camera.position = player_ship.position

    # Update game state
    for ship in ships:
        ship.update_position(delta_time)
        ship.update_weapons(delta_time)

    # Check for ship-ship collisions
    for i in range(len(ships)):
        for j in range(i + 1, len(ships)):
            ship1 = ships[i]
            ship2 = ships[j]
            if check_ship_collision(ship1, ship2):
                handle_ship_collision(ship1, ship2)

    for projectile in projectiles:
        if isinstance(projectile, HomingMissile):
            projectile.update(delta_time, ships)
        else:
            projectile.update(delta_time)

    # Update explosions and particles
    explosions.update(delta_time)
    particles.update(delta_time)

    # Check for projectile-ship collisions
    for ship in ships:
        for projectile in projectiles:
            # if projectile.origin_race != ship.race and check_projectile_collision(ship, projectile):
            if projectile.origin_relationship != ship.relationship and check_projectile_collision(ship, projectile):
                handle_projectile_collision(ship, projectile)

    # Check for attached laser-ship collisions
    for ship in ships:
        for other_ship in ships:
            if ship != other_ship:
                for weapon_slot in ['primary_weapon', 'secondary_weapon', 'special_weapon']:
                    weapon = getattr(ship, weapon_slot, None)
                    if isinstance(weapon, TrazerWeapon):
                        for laser in weapon.attached_lasers:
                            if laser.origin_relationship != ship.relationship:
                                # Swap parameters to get offset in laser's coordinate space
                                offset = pygame.sprite.collide_mask(laser, other_ship)
                                if offset:
                                    # Calculate collision position in the laser's coordinate space
                                    collision_position = laser.rect.topleft + pygame.math.Vector2(offset)
                                    handle_attached_laser_collision(other_ship, laser, collision_position)

    # Handle ships with zero or negative health
    for ship in ships[:]:
        if ship.health <= 0:
            # Play explosion sound
            sound_manager.play_sound('explosion')

            # Create a ship explosion at the ship's position
            explosion = Explosion(
                position=ship.position,
                sprite_sheet=ship_explosion_sprite_sheet,  # Use ship explosion assets
                frames=ship_explosion_frames,
                size=ship.size_scale,  # Adjust size as needed
                duration=1,                # Total duration of the explosion effect
                animation_speed=0.3          # Slow down the animation frames
            )
            explosions.add(explosion)

    # Remove ships with zero or negative health
    ships = [ship for ship in ships if ship.health > 0]

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw game elements using camera
    draw_grid(screen, camera)
    for ship in ships:
        ship.draw(screen, camera)
    for projectile in projectiles:
        projectile.draw(screen, camera)
    for explosion in explosions:
        explosion.draw(screen, camera)
    for particle in particles:
        particle.draw(screen, camera)

    # Flip the display
    pygame.display.flip()

