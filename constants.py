# constants.py - Global constants for the game

# City dimensions
BLOCK_SIZE = 20       # Each "city block" dimension (the land between roads)
ROAD_WIDTH = 10       # Width of each road
CELL_SPACING = BLOCK_SIZE + ROAD_WIDTH  # Distance between parallel roads' center lines
GRID_SIZE = 4         # 4×4 blocks => 5 parallel roads in each direction
OFFSET = -(GRID_SIZE // 2) * CELL_SPACING  # So city is centered around (0,0)

# Road arc parameters
ARC_RADIUS = 4        # Radius for smooth "right-turn" arcs at intersections
ARC_SEGMENTS = 10     # Number of quads per arc for smoother curves 