import pygame
import math
import random
import GeminiAPI

# Model classes
class Beacon:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class RobotState:
    def __init__(self):
        self.actions = []
        self.sensor_readings = []
        self.gemini_estimates = []

    def print_state(self):
        print("Actions:", self.actions)
        print("Sensor Readings:", self.sensor_readings)
        print("Gemini Estimates:", self.gemini_estimates)

class Robot:
    def __init__(self, x, y, theta, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.theta = theta
        self.color = color
        self.state = RobotState()
        self.step_size = 0.2

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.state.actions.append('w')

    def rotate(self, dtheta):
        self.theta += dtheta
        self.state.actions.append('a' if dtheta > 0 else 'd')

    def dump_pose(self, visible_beacons):

        with open('localization_tests/test_data.txt', 'a') as f:
            f.write(f"- groundtruth pose: x={self.x:.2f}, y={self.y:.2f}, theta={math.degrees(self.theta):.1f}\n")

            f.write("- Visible beacons:\n")
            for data in visible_beacons:
                if data['visible']:
                    beacon = data['beacon']
                    f.write(f"  Beacon {beacon.id}: d={data['distance']:.2f}m, θ={math.degrees(data['angle']):.1f}°\n")
            f.write("\n")

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
        self.shadow_robot = Robot(0, 0, 0, (128, 128, 128))

        self.wall = Wall(0, 0, 2.5)
        self.beacon_radius = 5

        self.beacons = []
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x = self.beacon_radius * math.cos(angle)
            y = self.beacon_radius * math.sin(angle)
            self.beacons.append(Beacon(i, x, y))

    def place_robot_random(self):

        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(self.wall.radius + 0.5, self.beacon_radius - 0.5)
        self.robot.x = radius * math.cos(angle)
        self.robot.y = radius * math.sin(angle)
        self.robot.theta = random.uniform(0, 2 * math.pi)

    def check_line_circle_intersection(self, x1, y1, x2, y2, circle_x, circle_y, circle_r):
        dx = x2 - x1
        dy = y2 - y1
        cx = circle_x - x1
        cy = circle_y - y1
        l2 = dx * dx + dy * dy

        if l2 == 0:
            return math.sqrt(cx * cx + cy * cy) <= circle_r

        t = max(0, min(1, (cx * dx + cy * dy) / l2))
        projection_x = x1 + t * dx
        projection_y = y1 + t * dy
        distance = math.sqrt(
            (circle_x - projection_x) ** 2 +
            (circle_y - projection_y) ** 2
        )
        return distance <= circle_r

    def update_shadow_robot(self):
        try:
            x, y, theta = GeminiAPI.get_state_vector()
            self.shadow_robot.x = x
            self.shadow_robot.y = y
            self.shadow_robot.theta = math.radians(theta)
            self.robot.state.gemini_estimates.append((x, y, math.radians(theta)))

        except Exception as e:
            print(f"Error updating shadow robot: {e}")

    def is_beacon_visible(self, beacon):
        return not self.check_line_circle_intersection(
            self.robot.x, self.robot.y,
            beacon.x, beacon.y,
            self.wall.x, self.wall.y, self.wall.radius
        )

    def calculate_angle_and_distance(self, beacon):
        dx = beacon.x - self.robot.x
        dy = beacon.y - self.robot.y
        distance = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx) - self.robot.theta
        angle = (angle + math.pi) % (2 * math.pi) - math.pi
        return distance, angle

    def get_visible_beacons(self):
        beacon_data = []
        for beacon in self.beacons:
            visible = self.is_beacon_visible(beacon)
            distance, angle = self.calculate_angle_and_distance(beacon)
            beacon_data.append({
                'beacon': beacon,
                'visible': visible,
                'distance': distance,
                'angle': angle
            })
        return beacon_data

    def generate_localization_prompt(self):
        sensor_data = {
            'visible_beacons': self.get_visible_beacons(),
            'robot': self.robot,
            'wall': {
                'x': self.wall.x,
                'y': self.wall.y,
                'radius': self.wall.radius
            },
            'beacon_radius': self.beacon_radius
        }
        return GeminiAPI.generate_prompt(sensor_data)

class Visualization:
    def __init__(self, width=1000, height=900):
        pygame.init()
        pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Robot Environment with Line of Sight")

        self.width = width
        self.height = height
        self.simulation_height = 800

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.GRAY = (128, 128, 128)

        self.scale = 50

        self.font = pygame.font.Font(None, 24)

        self.random_button = Button(
            20, self.simulation_height + 20,
            160, 40,
            "Random Position",
            self.font
        )
        self.localize_button = Button(
            200, self.simulation_height + 20,
            160, 40,
            "Localize",
            self.font
        )

        self.dump_button = Button(
            380, self.simulation_height + 20,
            160, 40,
            "Dump Pose",
            self.font
        )

    def world_to_screen(self, x, y):
        screen_x = self.width // 2 + int(x * self.scale)
        screen_y = self.simulation_height // 2 - int(y * self.scale)
        return screen_x, screen_y

    def draw_text(self, text, position, color=None):
        if color is None:
            color = self.BLACK
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)


    def draw(self, world):
        self.screen.fill(self.WHITE)

        wall_pos = self.world_to_screen(world.wall.x, world.wall.y)
        pygame.draw.circle(
            self.screen,
            self.BLACK,
            wall_pos,
            int(world.wall.radius * self.scale),
        )

        robot_pos = self.world_to_screen(world.robot.x, world.robot.y)
        shadow_pos = self.world_to_screen(world.shadow_robot.x, world.shadow_robot.y)

        # connections to beacons
        beacon_data = world.get_visible_beacons()
        for data in beacon_data:
            beacon = data['beacon']
            beacon_pos = self.world_to_screen(beacon.x, beacon.y)

            color = self.GREEN if data['visible'] else self.GRAY
            pygame.draw.aaline(self.screen, color, robot_pos, beacon_pos)

            pygame.draw.circle(self.screen, self.BLUE, beacon_pos, 5)

            if data['visible']:
                self.draw_text(
                    f"Beacon {beacon.id}",
                    (beacon_pos[0] + 10, beacon_pos[1] - 20)
                )
                self.draw_text(
                    f"d={data['distance']:.1f}m",
                    (beacon_pos[0] + 10, beacon_pos[1])
                )
                self.draw_text(
                    f"θ={math.degrees(data['angle']):.1f}°",
                    (beacon_pos[0] + 10, beacon_pos[1] + 20)
                )
            else:
                self.draw_text(
                    f"Beacon {beacon.id}",
                    (beacon_pos[0] + 10, beacon_pos[1] - 10)
                )

        pygame.draw.circle(self.screen, world.robot.color, robot_pos, 15)
        pygame.draw.circle(self.screen, world.shadow_robot.color, shadow_pos, 15)

        indicator_length = 20
        end_x = robot_pos[0] + int(indicator_length * math.cos(world.robot.theta))
        end_y = robot_pos[1] - int(indicator_length * math.sin(world.robot.theta))
        pygame.draw.aaline(self.screen, self.GREEN, robot_pos, (end_x, end_y), 3)

        shadow_end_x = shadow_pos[0] + int(indicator_length * math.cos(world.shadow_robot.theta))
        shadow_end_y = shadow_pos[1] - int(indicator_length * math.sin(world.shadow_robot.theta))
        pygame.draw.aaline(self.screen, self.GREEN, shadow_pos, (shadow_end_x, shadow_end_y), 3)

        self.random_button.draw(self.screen)
        self.localize_button.draw(self.screen)
        self.dump_button.draw(self.screen)


        config_text = [
            f"Robot Configuration:",
            f"x: {world.robot.x:.2f} m",
            f"y: {world.robot.y:.2f} m",
            f"θ: {math.degrees(world.robot.theta):.1f}°"
        ]

        shadow_config_text = [
            f"Shadow Robot Configuration:",
            f"x: {world.shadow_robot.x:.2f} m",
            f"y: {world.shadow_robot.y:.2f} m",
            f"θ: {math.degrees(world.shadow_robot.theta):.1f}°"
        ]

        for i, text in enumerate(config_text):
            self.draw_text(
                text,
                (500, self.simulation_height + 20 + i * 20),
                self.BLACK
            )

        for i, text in enumerate(shadow_config_text):
            self.draw_text(
                text,
                (700, self.simulation_height + 20 + i * 20),
                self.GRAY
            )

class Application:
    def __init__(self):
        self.world = World()
        self.vis = Visualization()

    def handle_input(self):
        step_size = 0.4
        update_occurred = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.vis.random_button.is_clicked(event.pos):
                        self.world.place_robot_random()
                        update_occurred = True
                    elif self.vis.localize_button.is_clicked(event.pos):
                        GeminiAPI.call_gemini()
                        self.world.update_shadow_robot()
                        update_occurred = True
                    elif self.vis.dump_button.is_clicked(event.pos):
                        print("dumping")
                        self.world.robot.dump_pose(self.world.get_visible_beacons())

            elif event.type == pygame.KEYDOWN:
                self.world.robot.state.sensor_readings.append(self.world.get_visible_beacons())
                if event.key == pygame.K_a:
                    self.world.robot.rotate(math.pi / 4)
                    update_occurred = True
                elif event.key == pygame.K_d:
                    self.world.robot.rotate(-math.pi / 4)
                    update_occurred = True
                elif event.key == pygame.K_w:
                    dx = step_size * math.cos(self.world.robot.theta)
                    dy = step_size * math.sin(self.world.robot.theta)
                    self.world.robot.move(dx, dy)
                    update_occurred = True

        if update_occurred:
            self.world.generate_localization_prompt()
            self.world.robot.state.print_state()
            GeminiAPI.call_gemini()
            self.world.update_shadow_robot()

        return True

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_input()
            self.vis.draw(self.world)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = Application()
    app.run()