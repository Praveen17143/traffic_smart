# car.py - Vehicle components for the driving simulation

from ursina import Entity, Vec3, color, time, held_keys, lerp, clamp, Text
from constants import OFFSET, CELL_SPACING, ROAD_WIDTH

class Car(Entity):
    """
    A drivable car with:
      - W/S for forward/back
      - A/D for left/right
      - Space for hand brake
    Very slow top speed & deceleration for easier city driving.
    """
    def __init__(self, roads, **kwargs):
        super().__init__(
            model='cube',
            scale=(1.5, 0.5, 3),
            color=color.rgb(220,20,60),  # Ferrari red
            position=(OFFSET + 3*CELL_SPACING, 0.3, OFFSET + ROAD_WIDTH*0.35),  # near bottom row
            rotation_y=90,  # face east
            **kwargs
        )
        self.roads = roads
        # Slower speeds
        self.speed = 0
        self.acceleration = 1
        self.max_speed = 5
        self.turn_speed = 100  # gentler turning

        self.create_wheels()
        
        # Create speedometer UI
        self.speedometer = Text(
            text="Speed: 0 km/h",
            position=(0, -0.4),
            origin=(0, 0),
            scale=1.5,
            color=color.white,
            background=True,
            background_color=color.black66
        )

    def create_wheels(self):
        """Attach 4 black cylinders as wheels."""
        front_z = 1.5
        back_z  = -1.5
        side_x  = 1.9
        wheel_r = 1.3
        wheel_w = 1.2

        wheel_positions = [
            ( side_x, -0.25, front_z),
            (-side_x, -0.25, front_z),
            ( side_x, -0.25, back_z),
            (-side_x, -0.25, back_z)
        ]
        for pos in wheel_positions:
            Entity(
                parent=self,
                model='cylinder',
                scale=(wheel_w, wheel_r*2, wheel_r*2),
                color=color.black,
                position=pos,
                rotation=(0,0,90)
            )

    def update(self):
        dt = time.dt

        # Forward/back
        if held_keys['w']:
            self.speed += self.acceleration * dt
        elif held_keys['s']:
            self.speed -= self.acceleration * dt
        else:
            # Very gentle deceleration
            self.speed = lerp(self.speed, 0, 1*dt)

        # Hand brake
        if held_keys['space']:
            self.speed = lerp(self.speed, 0, 10*dt)

        # Clamp speed
        self.speed = clamp(self.speed, -self.max_speed/2, self.max_speed)
        
        # Update speedometer (convert game speed to km/h for display)
        speed_kmh = abs(round(self.speed * 12))  # Adjusted conversion factor: max speed (5) * 12 = 60 km/h
        self.speedometer.text = f"Speed: {speed_kmh} km/h"

        # Steering
        direction = 0
        if held_keys['a']:
            direction = -1
        elif held_keys['d']:
            direction = 1
        turn_amount = direction * self.turn_speed * dt * (abs(self.speed)/self.max_speed)
        self.rotation_y += turn_amount

        # Move
        displacement = self.forward * self.speed * dt
        new_pos = self.position + displacement

        # Only move if on road
        from utilities import is_on_road
        if is_on_road(new_pos, self.roads):
            self.position = new_pos
        else:
            self.speed = 0 