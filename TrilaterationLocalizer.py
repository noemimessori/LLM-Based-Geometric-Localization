import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt


class RobotLocalizer:
    def __init__(self):
        self.beacons = np.array([
            [5.0, 0.0],  # Beacon 0
            [3.54, 3.54],  # Beacon 1
            [0.0, 5.0],  # Beacon 2
            [-3.54, 3.54],  # Beacon 3
            [-5.0, 0.0],  # Beacon 4
            [-3.54, -3.54],  # Beacon 5
            [0.0, -5.0],  # Beacon 6
            [3.54, -3.54]  # Beacon 7
        ])

        self.wall_radius = 2.5
        self.beacon_radius = 5.0

    def normalize_angle(self, angle):
        return np.mod(angle + np.pi, 2 * np.pi) - np.pi

    def residuals(self, state, measurements):

        x, y, theta = state
        residuals = []

        for beacon_id, dist, angle in measurements:
            beacon_pos = self.beacons[beacon_id]
            dx = beacon_pos[0] - x
            dy = beacon_pos[1] - y

            pred_dist = np.sqrt(dx ** 2 + dy ** 2)
            pred_angle = self.normalize_angle(np.arctan2(dy, dx) - theta)

            # Add distance residual
            residuals.append((pred_dist - dist) / 0.1)

            angle_diff = self.normalize_angle(pred_angle - angle)
            residuals.append(angle_diff / 0.05)

        r = np.sqrt(x ** 2 + y ** 2)
        if r < self.wall_radius:
            residuals.append(10 * (self.wall_radius - r))
        if r > self.beacon_radius:
            residuals.append(10 * (r - self.beacon_radius))

        return np.array(residuals)

    def estimate_initial_position(self, measurements):
        closest_measurement = min(measurements, key=lambda x: x[1])
        beacon_id, dist, angle = closest_measurement
        beacon_pos = self.beacons[beacon_id]

        theta_init = -angle  # Initial guess for orientation
        x_init = beacon_pos[0] - dist * np.cos(theta_init)
        y_init = beacon_pos[1] - dist * np.sin(theta_init)

        return np.array([x_init, y_init, theta_init])

    def localize(self, measurements):

        x0 = self.estimate_initial_position(measurements)
        result = least_squares(
            self.residuals,
            x0,
            args=(measurements,),
            method='lm',
            ftol=1e-8,
            xtol=1e-8
        )

        if not result.success:
            raise RuntimeError("Failed to converge to a solution")

        return result.x

    def plot_solution(self, state, measurements):
        plt.figure(figsize=(10, 10))
        plt.scatter(self.beacons[:, 0], self.beacons[:, 1],
                    c='blue', marker='^', label='Beacons')
        circle_wall = plt.Circle((0, 0), self.wall_radius,
                                 fill=False, color='gray')
        circle_beacon = plt.Circle((0, 0), self.beacon_radius,
                                   fill=False, color='gray')
        plt.gca().add_artist(circle_wall)
        plt.gca().add_artist(circle_beacon)

        x, y, theta = state
        plt.scatter(x, y, c='red', marker='o', label='Robot')
        arrow_length = 0.5
        dx = arrow_length * np.cos(theta)
        dy = arrow_length * np.sin(theta)
        plt.arrow(x, y, dx, dy, head_width=0.2, head_length=0.2, fc='r', ec='r')

        for beacon_id, dist, angle in measurements:
            beacon_pos = self.beacons[beacon_id]
            plt.plot([x, beacon_pos[0]], [y, beacon_pos[1]],
                     'g--', alpha=0.3)

        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.title('Robot Localization Solution')
        plt.show()


if __name__ == "__main__":
    localizer = RobotLocalizer()

    measurements = [
        (0, 6.43, np.radians(-174.2)),
        (1, 3.55, np.radians(-143.7)),
        (2, 0.91, np.radians(-42.8)),
        (3, 3.61, np.radians(54.0)),
        (4, 6.48, np.radians(84.3))
    ]

    try:
        solution = localizer.localize(measurements)
        print("\nEstimated robot state:")
        print(f"x: {solution[0]:.2f} m")
        print(f"y: {solution[1]:.2f} m")
        print(f"θ: {np.degrees(solution[2]):.1f}°")

        localizer.plot_solution(solution, measurements)

    except RuntimeError as e:
        print(f"Error: {e}")