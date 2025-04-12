from ursina import *
from math import sin, cos, radians, degrees, atan2
import random
import json
import os

# ---------------------------------------------------------------------
# GLOBAL CONSTANTS
# ---------------------------------------------------------------------

BLOCK_SIZE = 20       # Each "city block" dimension (the land between roads).
ROAD_WIDTH = 10       # Width of each road.
CELL_SPACING = BLOCK_SIZE + ROAD_WIDTH  # Distance between parallel roads' center lines.
GRID_SIZE = 2         # 2×2 blocks => 3 parallel roads in each direction.
OFFSET = -(GRID_SIZE // 2) * CELL_SPACING  # So city is centered around (0,0).

# Angle threshold (in degrees) for considering a traffic light as "in front"
ANGLE_THRESHOLD = 15

# ---------------------------------------------------------------------
# PERSISTENT SCORE HELPERS
# ---------------------------------------------------------------------

SCORE_FILE = 'score.json'

def load_score():
    """Load the saved score from disk, or return 100 if no file exists or on error."""
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('score', 100)
        except Exception as e:
            print(f"Error loading score, defaulting to 100: {e}")
    return 100

def save_score(score):
    """Write the current score to disk."""
    try:
        with open(SCORE_FILE, 'w') as f:
            json.dump({'score': score}, f)
    except Exception as e:
        print(f"Error saving score: {e}")

# ---------------------------------------------------------------------
# ROAD CLASSES
# ---------------------------------------------------------------------

class RoadSegment(Entity):
    def __init__(self, center, size, **kwargs):
        super().__init__(
            model='quad',
            position=(center[0], 0.02, center[1]),
            rotation_x=90,
            scale=(size[0], size[1]),
            color=color.rgb(30, 30, 30),
            **kwargs
        )
        self.center2d = Vec2(center[0], center[1])
        self.half_size = Vec2(size[0]*0.5, size[1]*0.5)

    def contains_point(self, pos):
        p2 = Vec2(pos.x, pos.z)
        return (abs(p2.x - self.center2d.x) <= self.half_size.x and
                abs(p2.y - self.center2d.y) <= self.half_size.y)

class RoadArc(Entity):
    def __init__(self, center, radius, start_angle, end_angle, width, segments=10, **kwargs):
        super().__init__(**kwargs)
        # Not used here.

# ---------------------------------------------------------------------
# BUILDINGS
# ---------------------------------------------------------------------

class WorkInProgress(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(position=position, **kwargs)
        self.cube = Entity(
            parent=self,
            model='cube',
            scale=(3, 1, 0.1),
            position=(0, 1.5, 0),
            color=color.gray,
            texture=load_texture('work_in_progress.jpg')
        )
        self.pole_left = Entity(
            parent=self.cube,
            model='cube',
            scale=(-0.1, 1, 0.1),
            color=color.black,
            position=(-0.3, -1, 0)
        )
        self.pole_right = Entity(
            parent=self.cube,
            model='cube',
            scale=(0.1, 1, 0.1),
            color=color.black,
            position=(0.3, -1, 0)
        )

class Building(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(position=(position[0], 0, position[1]), **kwargs)
        base_w, base_d, base_h, roof_h = 15, 15, 20, 8
        wall_tex = load_texture('building.jpg')
        roof_tex = load_texture('building.jpg')
        Entity(
            parent=self,
            model='cube',
            texture=wall_tex,
            scale=(base_w, base_h, base_d),
            position=(0, base_h*0.5, 0)
        )
        Entity(
            parent=self,
            model='cone',
            texture=roof_tex,
            scale=(base_w*1.2, roof_h, base_d*1.2),
            position=(0, base_h, 0)
        )

# ---------------------------------------------------------------------
# TRAFFIC LIGHT & SIGNS
# ---------------------------------------------------------------------

class StopSign(Entity):
    def __init__(self, position, rotation_y=0, **kwargs):
        super().__init__(position=position, rotation_y=rotation_y, **kwargs)
        Entity(parent=self, model='cube', scale=(0.1,4,0.1), color=color.black, position=(0,1,0))
        self.sign = Entity(parent=self, model='cube', scale=(1,1,0.1), color=color.white, position=(0,3.5,0))
        self.sign.texture = load_texture('stop_sign.jpg')

class SpeedLimitSign(Entity):
    def __init__(self, position, rotation_y=0, **kwargs):
        super().__init__(position=position, rotation_y=rotation_y, **kwargs)
        Entity(parent=self, model='cube', scale=(0.1,4,0.1), color=color.black, position=(0,1,0))
        self.sign = Entity(parent=self, model='cube', scale=(1,1,0.1), color=color.red, position=(0,3.5,0))
        self.sign.texture = load_texture('speed_limit.jpg')

class TrafficLight(Entity):
    def __init__(self, position, rotation_y=0, light_index=0, **kwargs):
        super().__init__(position=position, rotation_y=rotation_y, light_index=light_index, **kwargs)
        Entity(parent=self, model='cylinder', scale=(1,8,1), color=color.gray, position=(0,4,0))
        self.box = Entity(parent=self, model='cube', scale=(0.5,1,0.5), color=color.dark_gray, position=(0,7.5,0))
        self.red_light = Entity(parent=self.box, model='sphere', scale=0.4, color=color.rgb(50,0,0), position=(0,0.2,0.6))
        self.green_light = Entity(parent=self.box, model='sphere', scale=0.4, color=color.rgb(0,50,0), position=(0,-0.2,0.6))
        self.time_elapsed = 0

    def update(self):
        self.time_elapsed += time.dt
        if self.time_elapsed >= 20:
            self.time_elapsed = 0
            if self.light_index == 0:
                self.light_index = 1
                # When switching to red:
                self.red_light.color = color.rgb(255,0,0)
                self.green_light.color = color.rgb(0,50,0)
            else:
                self.light_index = 0
                # When switching to green:
                self.red_light.color = color.rgb(50,0,0)
                self.green_light.color = color.rgb(0,255,0)

    def is_red(self):
        """Returns True if the traffic light is red."""
        return self.light_index == 1

# ---------------------------------------------------------------------
# CAR
# ---------------------------------------------------------------------

class Car(Entity):
    def __init__(self, roads, initial_score=100, **kwargs):
        super().__init__(
            model='cube',
            scale=(1.5, 0.5, 3),
            color=color.rgb(220,20,60),
            position=(OFFSET + 1 * CELL_SPACING, 0.3, OFFSET + ROAD_WIDTH * 0.35),
            rotation_y=90,
            **kwargs
        )
        self.roads = roads
        self.speed = 0
        self.acceleration = 1
        self.max_speed = 5
        self.turn_speed = 100
        self.create_wheels()

        self.speedometer = Text(
            text="Speed: 0 km/h",
            position=(0, -0.4),
            origin=(0, 0),
            scale=1.2,
            color=color.white,
            background=True,
            background_color=color.black66
        )

        # initialize persistent score
        self.player_score_value = initial_score
        self.player_score = Text(
            text=f"SCORE {self.player_score_value}",
            position=(0.6, 0.4),
            origin=(0, 0),
            scale=1.5,
            color=color.white,
            background=True,
            background_color=color.black10
        )

        self.penalty_timer = 0
        self.work_penalty_timer = 0
        self.traffic_penalty_timer = 0  # timer for traffic light rule

    def create_wheels(self):
        front_z, back_z = 1.5, -1.5
        side_x, wheel_r, wheel_w = 1.9, 1.3, 1.2
        for pos in [(side_x, -0.25, front_z),
                    (-side_x, -0.25, front_z),
                    (side_x, -0.25, back_z),
                    (-side_x, -0.25, back_z)]:
            Entity(parent=self, model='cylinder', scale=(wheel_w, wheel_r * 2, wheel_r * 2),
                   color=color.black, position=pos, rotation=(0, 0, 90))

    def change_score(self, delta):
        self.player_score_value += delta
        self.player_score.text = f"SCORE {self.player_score_value}"
        save_score(self.player_score_value)

    def update(self):
        dt = time.dt
        # Acceleration / braking
        if held_keys['w']:
            self.speed += self.acceleration * dt
        elif held_keys['s']:
            self.speed -= self.acceleration * dt
        else:
            self.speed = lerp(self.speed, 0, 1 * dt)
        if held_keys['space']:
            self.speed = lerp(self.speed, 0, 10 * dt)
        self.speed = clamp(self.speed, -self.max_speed / 2, self.max_speed)

        speed_kmh = abs(round(self.speed * 12))
        self.speedometer.text = f"Speed: {speed_kmh} km/h"

        # Steering
        direction = (-1 if held_keys['a'] else 1) if held_keys['d'] or held_keys['a'] else 0
        turn_amount = direction * self.turn_speed * dt * (abs(self.speed) / self.max_speed)
        self.rotation_y += turn_amount

        # Movement
        new_pos = self.position + self.forward * self.speed * dt
        if is_on_road(new_pos, self.roads):
            self.position = new_pos
        else:
            self.speed = 0

        # Speed limit check
        if abs(distance(self.position, speed_limit_signs[0].position)) < 15:
            if speed_kmh > 30:
                speed_warning.text = "Speed limit 30, do not exceed!"
                speed_warning.color = color.red
                self.penalty_timer += dt
                if self.penalty_timer >= 1:
                    self.change_score(-1)
                    self.penalty_timer = 0
            else:
                speed_warning.text = "Good job! Following speed limit!"
                speed_warning.color = color.green
                self.penalty_timer += dt
                if self.penalty_timer >= 1:
                    self.change_score(+1)
                    self.penalty_timer = 0
        else:
            speed_warning.text = ""
            self.penalty_timer = 0

        # Work in progress / stop sign check
        for sign in stop_signs:
            if abs(distance(self.position, sign.position)) < 15:
                work_warning.text = "STOP: Work In Progress"
                self.work_penalty_timer += dt
                if self.work_penalty_timer >= 1:
                    self.change_score(-1)
                    self.work_penalty_timer = 0
                break
        else:
            work_warning.text = ""
            self.work_penalty_timer = 0

        # Traffic light check using a cone-of-vision approach.
        # Compute the vector to the light.
        traffic_found = False
        for light in traffic_lights:
            to_light = light.position - self.position
            # Only consider if the light is in front of the car.
            forward_distance = self.forward.dot(to_light)
            if forward_distance <= 0 or to_light.length() >= 15:
                continue

            # Compute the lateral distance in the car's local coordinates.
            # Compute the right vector as perpendicular to forward in the xz-plane.
            right_vector = Vec3(self.forward.z, 0, -self.forward.x)
            lateral_distance = abs(right_vector.dot(to_light))
            
            # Alternatively compute the angle between forward and to_light.
            angle = degrees(atan2(lateral_distance, forward_distance))
            
            if angle < ANGLE_THRESHOLD:
                traffic_found = True
                if light.is_red():
                    # At red light, the car should be nearly stopped.
                    if speed_kmh > 1:
                        traffic_warning.text = "Red Light! Stop the car!"
                        traffic_warning.color = color.red
                        self.traffic_penalty_timer += dt
                        if self.traffic_penalty_timer >= 1:
                            self.change_score(-1)
                            self.traffic_penalty_timer = 0
                    else:
                        traffic_warning.text = "Stopped at red light, good job!"
                        traffic_warning.color = color.green
                        self.traffic_penalty_timer += dt
                        if self.traffic_penalty_timer >= 1:
                            self.change_score(+1)
                            self.traffic_penalty_timer = 0
                else:
                    # At green light, the car should be moving.
                    if speed_kmh > 1:
                        traffic_warning.text = "Green Light! Keep going!"
                        traffic_warning.color = color.green
                        self.traffic_penalty_timer += dt
                        if self.traffic_penalty_timer >= 1:
                            self.change_score(+1)
                            self.traffic_penalty_timer = 0
                    else:
                        traffic_warning.text = "Green Light! You should move!"
                        traffic_warning.color = color.red
                        self.traffic_penalty_timer += dt
                        if self.traffic_penalty_timer >= 1:
                            self.change_score(-1)
                            self.traffic_penalty_timer = 0
                break
        if not traffic_found:
            traffic_warning.text = ""
            self.traffic_penalty_timer = 0

# ---------------------------------------------------------------------
# HELPERS & CITY SETUP
# ---------------------------------------------------------------------

def is_on_road(pos, roads):
    return any(r.contains_point(pos) for r in roads)

def create_crossing_stripes(x, z, orientation, num_stripes=7, stripe_thickness=1, gap=0.5):
    total_length = num_stripes * stripe_thickness + (num_stripes - 1) * gap
    start = -total_length / 2 + stripe_thickness / 2
    if orientation == 'horizontal':
        for i in range(num_stripes):
            Entity(model='quad', scale=(3, stripe_thickness),
                   position=(x, 0.03, z + start + i * (stripe_thickness + gap)),
                   rotation_x=90, color=color.white)
    else:
        for i in range(num_stripes):
            Entity(model='quad', scale=(stripe_thickness, 3),
                   position=(x + start + i * (stripe_thickness + gap), 0.03, z),
                   rotation_x=90, color=color.white)

def create_center_crosswalks():
    cx = OFFSET + CELL_SPACING
    cz = OFFSET + CELL_SPACING
    off = ROAD_WIDTH - 1.5
    create_crossing_stripes(cx, cz + off, 'vertical')
    create_crossing_stripes(cx, cz - off, 'vertical')
    create_crossing_stripes(cx + off, cz, 'horizontal')
    create_crossing_stripes(cx - off, cz, 'horizontal')

def create_traffic_lights():
    lights = []
    cx, cz = OFFSET + CELL_SPACING, OFFSET + CELL_SPACING
    lights.append(TrafficLight(position=(cx + ROAD_WIDTH / 2, -3, cz), rotation_y=90, light_index=0))
    lights.append(TrafficLight(position=(cx, -3, cz + ROAD_WIDTH / 2), rotation_y=0, light_index=1))
    lights.append(TrafficLight(position=(cx - ROAD_WIDTH / 2, -3, cz), rotation_y=-90, light_index=1))
    lights.append(TrafficLight(position=(cx, -3, cz - ROAD_WIDTH / 2), rotation_y=180, light_index=0))
    return lights

def create_speed_limit_signs():
    return [ SpeedLimitSign(position=(OFFSET - ROAD_WIDTH * 0.4, 0, OFFSET + CELL_SPACING)) ]

def create_stop_signs():
    lst = []
    lst.append(StopSign(position=(OFFSET - 2 + 2 * CELL_SPACING, 0, OFFSET + 2 * CELL_SPACING), rotation_y=90))
    lst.append(StopSign(position=(OFFSET + 2 * CELL_SPACING, 0, OFFSET - 2 + 0 * CELL_SPACING), rotation_y=90))
    lst.append(WorkInProgress(position=(OFFSET + 2 * CELL_SPACING, 0, OFFSET + CELL_SPACING), rotation_y=90))
    return lst

def create_city():
    for j in range(GRID_SIZE + 1):
        z = OFFSET + j * CELL_SPACING
        roads.append(RoadSegment(center=(0, z), size=(GRID_SIZE * CELL_SPACING, ROAD_WIDTH)))
    for i in range(GRID_SIZE + 1):
        x = OFFSET + i * CELL_SPACING
        roads.append(RoadSegment(center=(x, 0), size=(ROAD_WIDTH, GRID_SIZE * CELL_SPACING)))
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            bx = OFFSET + i * CELL_SPACING + CELL_SPACING * 0.5
            bz = OFFSET + j * CELL_SPACING + CELL_SPACING * 0.5
            Building(position=(bx, bz))
    create_center_crosswalks()
    global speed_limit_signs, stop_signs
    speed_limit_signs = create_speed_limit_signs()
    stop_signs = create_stop_signs()
    return create_traffic_lights()

# ---------------------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------------------

app = Ursina()
window.color = color.black
from ursina.prefabs.sky import Sky
Sky(color=color.rgb(80, 160, 255))
AmbientLight(color=color.rgb(180,180,180))
DirectionalLight(direction=(1,-1,1), color=color.white)

ground = Entity(
    model='cube', scale=(100,1,100), position=(0,-0.5,0),
    color=color.rgb(40,40,40), texture='white_cube', texture_scale=(50,50)
)

roads = []
traffic_lights = create_city()

# Warning texts for various checks:
speed_warning = Text(text="", position=(0,0.2), scale=2, color=color.red, origin=(0,0))
work_warning  = Text(text="", position=(0,0.4), scale=2, color=color.red, origin=(0,0))
traffic_warning = Text(text="", position=(0,-0.2), scale=2, color=color.red, origin=(0,0))

# Load persistent score (or default to 100)
starting_score = load_score()
car = Car(roads=roads, initial_score=starting_score)

def update():
    car.update()
    for light in traffic_lights:
        light.update()
    offset = car.forward * -5 + Vec3(0,3,0)
    camera.position = car.position + offset
    camera.look_at(car.position + car.forward * 10)

app.run()
