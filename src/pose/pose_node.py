class PoseNode:
    def __init__(self, x: float, y: float, z: float, name: str):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
    
    def __repr__(self):
        return f"PoseNode(name='{self.name}', x={self.x}, y={self.y}, z={self.z})"
