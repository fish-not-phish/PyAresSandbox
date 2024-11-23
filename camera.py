import pygame

class Camera:
    def __init__(self, width, height):
        self.position = pygame.math.Vector2(0, 0)  # Center of the camera in the game world
        self.zoom_level = 1.0  # Initial zoom level
        self.width = width  # Viewport width
        self.height = height  # Viewport height

    def world_to_screen(self, world_position):
        """
        Convert world coordinates to screen coordinates based on the camera position and zoom level.
        """
        screen_x = (world_position.x - self.position.x) * self.zoom_level + self.width / 2
        screen_y = (world_position.y - self.position.y) * self.zoom_level + self.height / 2
        return pygame.math.Vector2(screen_x, screen_y)

    def screen_to_world(self, screen_position):
        """
        Convert screen coordinates to world coordinates based on the camera position and zoom level.
        """
        world_x = (screen_position.x - self.width / 2) / self.zoom_level + self.position.x
        world_y = (screen_position.y - self.height / 2) / self.zoom_level + self.position.y
        return pygame.math.Vector2(world_x, world_y)

    def adjust_zoom(self, delta_zoom):
        """
        Adjust the zoom level and clamp it to reasonable bounds.
        """
        self.zoom_level = max(0.1, self.zoom_level + delta_zoom)
