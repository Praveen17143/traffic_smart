# utilities.py - Utility functions for the driving simulation

def is_on_road(pos, roads):
    """Return True if pos lies on any road or arc."""
    for r in roads:
        if r.contains_point(pos):
            return True
    return False

def create_city(roads, constants):
    """
    Create a 4×4 grid of roads with buildings in each block.
    
    Args:
        roads: List to append road segments to
        constants: Module containing city constants
    """
    from buildings import Building
    from roads import RoadSegment
    
    # Import constants
    OFFSET = constants.OFFSET 
    GRID_SIZE = constants.GRID_SIZE
    CELL_SPACING = constants.CELL_SPACING
    ROAD_WIDTH = constants.ROAD_WIDTH
    
    # 1) Create horizontal roads
    for j in range(GRID_SIZE+1):
        z = OFFSET + j*CELL_SPACING
        center = (0, z)
        length = (GRID_SIZE * CELL_SPACING)
        # RoadSegment with center at x=0, covers x in [-length/2 .. length/2]
        roads.append(RoadSegment(
            center=center,
            size=(length, ROAD_WIDTH)
        ))

    # 2) Create vertical roads
    for i in range(GRID_SIZE+1):
        x = OFFSET + i*CELL_SPACING
        center = (x, 0)
        length = (GRID_SIZE * CELL_SPACING)
        roads.append(RoadSegment(
            center=center,
            size=(ROAD_WIDTH, length)
        ))
    
    # 3) Create buildings in each block
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            # Center of block = (ix + half spacing, iz + half spacing)
            bx = OFFSET + i*CELL_SPACING + (CELL_SPACING*0.5)
            bz = OFFSET + j*CELL_SPACING + (CELL_SPACING*0.5)
            Building(position=(bx, bz))
            
    return roads