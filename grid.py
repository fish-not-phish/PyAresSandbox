import pygame

def draw_grid(surface, camera):
    if camera.zoom_level > 0.8:  # Hide grid when zoomed in
        return
    base_spacing = 50  # Base spacing for the smallest grid in world units
    zoom_threshold = 0.5  # Zoom level at which grid zones start merging
    zone_multiplier = 1  # Multiplier for merging smaller zones into larger ones

    # Adjust spacing based on the zoom level
    if camera.zoom_level < zoom_threshold:
        zone_multiplier = int(1 / camera.zoom_level)  # Merge smaller zones into larger ones
        zone_multiplier = max(1, zone_multiplier)  # Ensure at least one zone multiplier
    spacing = base_spacing * zone_multiplier

    # Determine the visible area in world coordinates
    top_left_world = camera.screen_to_world(pygame.math.Vector2(0, 0))
    bottom_right_world = camera.screen_to_world(
        pygame.math.Vector2(surface.get_width(), surface.get_height())
    )

    # Round the grid lines to the nearest multiple of spacing
    start_x = int(top_left_world.x // spacing) * spacing
    end_x = int(bottom_right_world.x // spacing + 1) * spacing
    start_y = int(top_left_world.y // spacing) * spacing
    end_y = int(bottom_right_world.y // spacing + 1) * spacing

    # Draw vertical lines
    for x in range(start_x, end_x, spacing):
        screen_x = (x - camera.position.x) * camera.zoom_level + camera.width / 2
        pygame.draw.line(surface, (50, 50, 50), (screen_x, 0), (screen_x, surface.get_height()))

    # Draw horizontal lines
    for y in range(start_y, end_y, spacing):
        screen_y = (y - camera.position.y) * camera.zoom_level + camera.height / 2
        pygame.draw.line(surface, (50, 50, 50), (0, screen_y), (surface.get_width(), screen_y))