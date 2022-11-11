import numpy as np
from .geometry import Object3D, Triangle, Vertex
import xml.etree.ElementTree as ET

class DAEParser:
    """
    Class to gather all the logic used to read and write to .dae files.
    """
    def __init__(self, filename):
        """
        Create an XML tree to navegate through the .dae file.
        """
        self._tree = ET.parse(filename)
        self._root = self._tree.getroot()
        self._ns = {'': 'http://www.collada.org/2005/11/COLLADASchema'}

    def parse_objects(self):
        """
        Search all 3D objects defined in the scene and parse its mesh, 
        retrieving then with all their colored faces.
        """
        objects = []
        for node in self._root.findall('./library_visual_scenes/visual_scene/node', self._ns):
            name = node.get('name')
            instance_geometry = node.find('instance_geometry', self._ns)
            geometry_id = instance_geometry.get('url')[1:]

            matrix = node.find('matrix', self._ns)
            transf_matrix = []
            for n in matrix.text.split():
                transf_matrix.append(float(n))
            transf_matrix = np.reshape(transf_matrix, (4,4))

            object = Object3D(name, geometry_id)

            for geometry in self._root.findall('./library_geometries/geometry', self._ns):
                vertices = []
                colors = []
                id = geometry.get('id')
                if id == geometry_id:
                    for source in geometry.findall('./mesh/source', self._ns):
                        source_id = source.get('id')

                        if source_id == geometry_id + '-positions':
                            vertices_elem = source.find('float_array', self._ns)
                            vertices_list = vertices_elem.text.split()
                            for i in range(0, len(vertices_list), 3):
                                v = np.array([
                                    float(vertices_list[i]),
                                    float(vertices_list[i+1]),
                                    float(vertices_list[i+2]), 1])
                                v = transf_matrix @ v.T
                                vertices.append(v[0:3])

                        if source_id == geometry_id + '-colors-Color':
                            colors_elem = source.find('float_array', self._ns)
                            colors_list = colors_elem.text.split()
                            for i in range(0, len(colors_list), 4):
                                colors.append(np.array([
                                    float(colors_list[i]),
                                    float(colors_list[i+1]),
                                    float(colors_list[i+2])
                                ]))
                
                    triangles = geometry.find('./mesh/triangles/p', self._ns)
                    t_list = triangles.text.split()
                    triangle_vertices = []
                    for i in range(0, len(t_list), 4):
                        vert_index = int(t_list[i])
                        color_index = int(t_list[i+3])
                        pos = vertices[vert_index]
                        color = colors[color_index]
                        triangle_vertices.append(Vertex(pos, color_index, color))
                        if len(triangle_vertices) == 3:
                            t = Triangle(triangle_vertices)
                            if t.is_valid():
                                object.add_triangle(t)
                            triangle_vertices = []
            
            objects.append(object)
        return objects

    def overwrite_object(self, object):
        """
        Write information of a modified object to the XML tree of the parser.
        """
        geometry_id = object.geometry_id
        for source in self._root.findall('./library_geometries/geometry/mesh/source', self._ns):
            if geometry_id + '-colors-Color' == source.get('id'):
                colors_elem = source.find('float_array', self._ns)
                colors_list = colors_elem.text.split()
                # print('Before updating', colors_list)
                for triangle in object.get_triangles():
                    for vertex in triangle.vertices:
                        c_idx = vertex.color_index
                        colors_list[4*c_idx:4*c_idx+3] = triangle.color.astype(str).tolist()
                # print('After updating', colors_list)

                # Removing A component for RGBA
                idx_for_A = list(range(3, len(colors_list), 4))
                idx_for_A.reverse()
                for i in idx_for_A:
                    del colors_list[i]
                colors_elem.set('count', str(len(colors_list)))
                accessor = source.find('./technique_common/accessor', self._ns)
                for color_param in accessor.findall('./param', self._ns):
                    if color_param.get('name') == "A":
                        accessor.remove(color_param)
                accessor.set('stride', "3")
                
                colors_elem.text = " ".join(colors_list)

    def save_file_to(self, file_path):
        """
        Save the XML tree back to a .dae file.
        """
        self._tree.write(file_path)

    @staticmethod
    def remove_namespace(file_path):
        """
        Remove the namespace from all of XML tags
        """
        with open(file_path, "r+") as f:
            data = f.read()
            f.seek(0)
            f.write(data.replace("ns0:", ""))
            f.truncate()

    @staticmethod
    def print_file(file_path):
        file = ET.parse(file_path).getroot()
        print(ET.tostring(file, encoding='unicode'))