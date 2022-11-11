import numpy as np

class Vertex:
    """
    Class to represent a vertex of the scene.
    """
    def __init__(self, pos, color_index, color):
        """
        Create a vertex with its position and color.
        """
        self._pos = pos
        self._color = color
        self.color_index = color_index
        self.x = self._pos[0]
        self.y = self._pos[1]
        self.z = self._pos[2]

    def __repr__(self):
        """
        Auxiliary function to print Vertex position.
        """
        return 'Vertex(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'
        
    def get_position(self):
        """
        Get the position of the vertex.
        """
        return self._pos

    def get_color(self):
        """
        Get the color of the vertex.
        """
        return self._color

class Triangle:
    """
    Class to represent a triangular face of the meshes in the scene.
    """
    def __init__(self, vertices):
        """
        Create a triangle with its vertices and calculates its normal vector,
        area, centroid and color as the mean value of its vertices' color.
        """
        self.vertices = vertices

        r1 = vertices[0].get_position()
        r2 = vertices[1].get_position()
        r3 = vertices[2].get_position()
        v = np.cross(r2-r1, r3-r1)
        if np.linalg.norm(v) == 0:
            self._valid = False
        else:
            self._valid = True
            self.normal = v / np.linalg.norm(v)

        self.area = np.linalg.norm(v) / 2
        self.centroid = (r1 + r2 +r3) / 3

        rho1 = vertices[0].get_color()
        rho2 = vertices[1].get_color()
        rho3 = vertices[2].get_color()
        self.color = (rho1 + rho2 + rho3) / 3

    def __repr__(self):
        """
        Auxiliary function to print Triangle with its vertices.
        """
        return 'Triangle(' + str(self.vertices[0]) + ', ' + str(self.vertices[1]) + ', ' + str(self.vertices[2]) + ')'

    def is_valid(self):
        """
        Check if the triangle is valid (area > 0).
        """
        return self._valid

    def set_color(self, c):
        """
        Change the color of the triangle face.
        """
        self.color = c

class Object3D:
    """
    Class to represent an object of the scene with its mesh.
    """
    def __init__(self, name, geometry_id):
        """
        Create an empty object just with its name and mesh id.
        """
        self.name = name
        self.geometry_id = geometry_id
        self._triangles = []

    def add_triangle(self, triangle):
        """
        Populate the object with a triangular face of its mesh.
        """
        self._triangles.append(triangle)
    
    def get_triangles(self):
        """
        Return all faces of the object's mesh.
        """
        return self._triangles
