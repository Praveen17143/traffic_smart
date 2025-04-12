# buildings.py - Building components for the city simulation

from ursina import Entity, load_texture

class Building(Entity):
    """
    A realistic building with a textured base and a conical roof.
    It uses textures downloaded from an indie game (or from OpenGameArt).
    """
    def __init__(self, position, **kwargs):
        # 'position' is a 2D tuple (x, z) for the block center.
        super().__init__(position=(position[0], 0, position[1]), **kwargs)
        # Dimensions for the building.
        base_width = 15
        base_depth = 15
        base_height = 20
        roof_height = 8

        # Load textures (ensure these files are in your assets folder or adjust the file names)
        wall_texture = load_texture('building.jpg')
        roof_texture = load_texture('building.jpg')

        # Building walls using the indie wall texture.
        self.walls = Entity(
            parent=self,
            model='cube',
            texture=wall_texture,
            scale=(base_width, base_height, base_depth),
            position=(0, base_height * 0.5, 0)
        )

        # Building roof using the indie roof texture.
        self.roof = Entity(
            parent=self,
            model='cone',
            texture=roof_texture,
            scale=(base_width * 1.2, roof_height, base_depth * 1.2),
            position=(0, base_height, 0)
        ) 