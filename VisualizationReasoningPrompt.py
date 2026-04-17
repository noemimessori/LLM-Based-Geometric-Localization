import pygame
import math

# Model classes
class Beacon:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class Robot:
    def __init__(self, x, y, theta, fov=math.radians(120), max_distance=6, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.theta = theta
        self.fov = fov
        self.max_distance = max_distance
        self.color = color

    def set_position(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

class Wall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.hover_color = (180, 180, 180)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class World:
    def __init__(self):
        self.robot = Robot(-3, 0, 0)
        self.wall = Wall(0, 0, 2.5)
        self.beacon_radius = 5
        self.beacons = [Beacon(i, self.beacon_radius * math.cos(i * (2 * math.pi / 8)), \
                            self.beacon_radius * math.sin(i * (2 * math.pi / 8))) for i in range(8)]

class Visualization:
    def __init__(self, width=1000, height=900):
        pygame.init()
        pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Robot Environment")
        self.width = width
        self.height = height
        self.simulation_height = 800
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (102, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.GEMINI = (204, 229, 255)
        self.GEMINIW = (0, 102, 204)
        self.CLAUDE = (255, 229, 204)
        self.CLAUDEW = (255, 128, 0)
        self.GPT = (204, 255, 204)
        self.GPTW = (0, 204, 0)
        self.LLAMA = (204, 255, 255)
        self.LLAMAW = (0, 204, 204)
        self.scale = 50
        self.font = pygame.font.Font(None, 24)
        self.buttons = [
            Button(870, 50 + i * 60, 110, 40, f"Position {i + 1}", self.font) for i in range(6)
        ]
        self.positions = [
            (-3.00, 0.00, 0.0),
            (-3.40, 0.00, 90.0),
            (-0.05, -3.75, 90.0),
            (2.96, -2.33, 135.0),
            (2.04, 1.88, 90.0),
            (-4.39, -1.89, 175.9),
        ]
        self.visible_beacons = [
            [2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6],
            [0, 4, 5, 6, 7],
            [0, 1, 5, 6, 7],
            [0, 1, 2],
            [2, 3, 4, 5, 6, 7],
        ]
        self.shadow_robots = {}
        self.colors = [self.GEMINI, self.CLAUDE, self.GPT, self.LLAMA]
        self.colors_estimate = [self.GEMINIW, self.CLAUDEW, self.GPTW, self.LLAMAW]
        self.timer = 0
        self.robot_sequence = []
        self.robot_index = 0

    def world_to_screen(self, x, y):
        screen_x = self.width // 2 + int(x * self.scale)
        screen_y = self.simulation_height // 2 - int(y * self.scale)
        return screen_x, screen_y

    def draw(self, world):
        self.screen.fill(self.WHITE)
        self.draw_text("Reasoning Prompt", (40, 40), self.BLACK)
        wall_pos = self.world_to_screen(world.wall.x, world.wall.y)
        pygame.draw.circle(self.screen, self.BLACK, wall_pos, int(world.wall.radius * self.scale))

        for i, beacon in enumerate(world.beacons):
            beacon_pos = self.world_to_screen(beacon.x, beacon.y)
            pygame.draw.circle(self.screen, self.BLUE, beacon_pos, 5)
            label = f"Beacon {beacon.id}"
            text_surface = self.font.render(label, True, self.BLACK)
            self.screen.blit(text_surface, (beacon_pos[0] + 10, beacon_pos[1] - 10))

            if i in self.visible_beacons[
                self.positions.index((world.robot.x, world.robot.y, math.degrees(world.robot.theta)))]:
                pygame.draw.line(self.screen, self.GREEN, self.world_to_screen(world.robot.x, world.robot.y),
                                 beacon_pos, 1)

                d = round(math.sqrt((beacon.x - world.robot.x) ** 2 + (beacon.y - world.robot.y) ** 2), 1)
                theta = round(math.degrees(math.atan2(beacon.y - world.robot.y, beacon.x - world.robot.x)), 1)
                detailed_label = [f"d={d}m", f"\u03b8={theta}°"]

                for j, line in enumerate(detailed_label):
                    offset_y = 10 + j * 15
                    detailed_surface = self.font.render(line, True, self.BLACK)
                    self.screen.blit(detailed_surface, (beacon_pos[0] + 10, beacon_pos[1] + offset_y))



        robot_pos = self.world_to_screen(world.robot.x, world.robot.y)
        pygame.draw.circle(self.screen, world.robot.color, robot_pos, 15)
        end_x = robot_pos[0] + int(20 * math.cos(world.robot.theta))
        end_y = robot_pos[1] - int(20 * math.sin(world.robot.theta))
        pygame.draw.line(self.screen, self.RED, robot_pos, (end_x, end_y), 2)

        for i, (name, coords) in enumerate(self.shadow_robots.items()):
            if i <= self.robot_index:
                shadow_pos = self.world_to_screen(coords[0], coords[1])
                pygame.draw.circle(self.screen, self.colors[i % len(self.colors)], shadow_pos, 15)
                # Draw angle
                end_x = shadow_pos[0] + int(20 * math.cos(math.radians(coords[2])))
                end_y = shadow_pos[1] - int(20 * math.sin(math.radians(coords[2])))
                pygame.draw.line(self.screen, self.colors_estimate[i % len(self.colors_estimate)], shadow_pos,
                                 (end_x, end_y), 2)

        for button in self.buttons:
            button.draw(self.screen)

        self.draw_configurations(world)

    def draw_configurations(self, world):
        # Robot configuration
        config_text = [
            f"Robot Configuration:",
            f"x: {world.robot.x:.2f} m",
            f"y: {world.robot.y:.2f} m",
            f"\u03b8: {math.degrees(world.robot.theta):.1f}°",
        ]

        shadow_config_text = []
        for i, (name, coords) in enumerate(self.shadow_robots.items()):
            if i <= self.robot_index:
                color = self.colors_estimate[i % len(self.colors_estimate)]
                shadow_config_text.append((
                    [
                        f"{name} Configuration:",
                        f"x: {coords[0]:.2f} m",
                        f"y: {coords[1]:.2f} m",
                        f"\u03b8: {coords[2]:.1f}°"
                    ],
                    color
                ))

        for i, text in enumerate(config_text):
            self.draw_text(
                text,
                (10, self.simulation_height + 10 + i * 20),
                self.RED
            )

        x_offset = 200
        for shadow_texts, color in shadow_config_text:
            for i, text in enumerate(shadow_texts):
                self.draw_text(
                    text,
                    (x_offset, self.simulation_height + 10 + i * 20),
                    color
                )
            x_offset += 200

    def draw_text(self, text, position, color):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def handle_click(self, pos, world):
        shadow_data = [
            {
                "Gemini": (-3, 0, 0), "Claude": (-3, 0, 0), "GPT": (-3, 0, 0), "Llama": (-3, 5.83, -59)
            },
            {
                "Gemini": (-3.4, 0, 0), "Claude": (-3.4, -1.6, 92.2), "GPT": (1.6, 0, 90), "Llama": (0, -2.5, -90)
            },
            {
                "Gemini": (0, -3.74, -87.5), "Claude": (0.2, -3.8, 2.5), "GPT": (0, -3.74, 0), "Llama": (-3.34, 0, 46.5)
            },
            {
                "Gemini": (3, -4, 170), "Claude": (4.5, -2.8, 70), "GPT": (3.6, -2.3, -70), "Llama": (-3, 0, 0)
            },
            {
                "Gemini": (2.5, 1.5, -20), "Claude": (2.5, 2.5, 75), "GPT": (2, 1.5, -45), "Llama": (3.17, 0, 0)
            },
            {
                "Gemini": (-2.7, -1.5, 150), "Claude": (-4.3, -2, -7.6), "GPT": (-5, 0, 121.7), "Llama": (-3, 0, 0)
            }
        ]
        for idx, button in enumerate(self.buttons):
            if button.is_clicked(pos):
                x, y, theta = self.positions[idx]
                world.robot.set_position(x, y, math.radians(theta))
                self.shadow_robots = shadow_data[idx]
                self.robot_sequence = list(self.shadow_robots.items())  # Sequence of robots
                self.robot_index = -1  # Start from before the first robot
                self.timer = pygame.time.get_ticks()  # Reset timer
                break

    def update_sequence(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.timer

        if elapsed_time > 1000 and self.robot_index < len(self.robot_sequence) - 1:  # 1 second delay
            self.robot_index += 1  # Move to the next robot in sequence
            self.timer = current_time  # Reset timer

def main():
    world = World()
    visualization = Visualization()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                visualization.handle_click(event.pos, world)

        visualization.update_sequence()
        visualization.draw(world)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
