import numpy as np
import os

class RadiositySystem:
    def __init__(self, all_triangles, lum_faces):
        """
        Class with all matematical parts of the radiosity linear system.
        A @ B = E
        """
        self._t = all_triangles
        self._n = len(all_triangles)
        self._NUM_COLORS = 3
        self._luminous_faces = lum_faces
        
        if not os.path.exists("./utils/numpy_files/A.npy"):
            self.A = self._calculate_A()
        else:
            file_A = open( "./utils/numpy_files/A.npy", 'rb')
            self.A = np.load(file_A)
        
        if not os.path.exists("./utils/numpy_files/E.npy"):
            self.E = self._calculate_E()
        else:
            file_E = open("./utils/numpy_files/E.npy", 'rb')
            self.E = np.load(file_E)
        
        self.B = np.empty((self._n, self._NUM_COLORS))

    def _calculate_A(self):
        """
        Calculate all elements A[i, j] of the left side of the radiosity linear system.
        A[i, j] = 1 - color * shape_factor, if i = j
        A[i, j] = - color * shape_factor, otherwhise
        """
        A = np.zeros((self._n, self._n, self._NUM_COLORS))
        for i, t_i in enumerate(self._t):
            for j, t_j in enumerate(self._t):
                if j == i:
                    A[i, i, :] += 1.0
                A[i, j, :] -= np.absolute(self._t[i].color * self._get_shape_factor(i, j))
        file_A = open("./utils/numpy_files/A.npy", 'wb')
        np.save(file_A, A)
        return A

    def _calculate_E(self):
        """
        Calculate all elements E[i] of the right side of the radiosity linear system.
        E[i] = 1, if i-th face is a luminous face
        E[i] = 0, otherwise
        """    
        E = np.zeros((self._n, self._NUM_COLORS))
        for idx_t, t in enumerate(self._t):
            for _, lum_t in enumerate(self._luminous_faces):
                if t == lum_t:
                    E[idx_t, :] = np.ones((1, self._NUM_COLORS))
                    break   
        file_E = open("./utils/numpy_files/E.npy", 'wb') 
        np.save(file_E, E)
        return E

    def _is_object_between(self, i, j):
        """
        Check if there is an object between two faces.
        """
        r_i = self._t[i].centroid
        r_j = self._t[j].centroid
        for triangle in self._t:
            t_vertices = triangle.vertices
            # A @ (t, u, v) = B
            A = np.zeros((3, 3))
            A[0] = r_j - r_i
            A[1] = t_vertices[1].get_position() - t_vertices[0].get_position()
            A[2] = t_vertices[2].get_position() - t_vertices[0].get_position()
            A = np.array(A)
            B = np.array(-r_j - t_vertices[0].get_position())
            det  = np.linalg.det(A)
            if det == 0:
                return True 
            else:
                t, u, v = np.linalg.solve(A, B)
                if 0 < t and t < 1:
                    if 0 < u and u < 1 and 0 < v and v < 1:
                        if v + u <= 1:
                            return True

    def _get_angle_between_faces(self, i, j):
        """
        Calculates the angle theta_j in RADIANS that is used to check if faces can see each other.
        """
        N_j = self._t[j].normal
        r = self._t[j].centroid - self._t[i].centroid
        norm_N_j = np.linalg.norm(N_j)
        norm_r = np.linalg.norm(r)   
        return np.arccos(np.clip(np.dot(N_j, r)/(norm_N_j * norm_r), -1.0, 1.0))

    def _get_shape_factor(self, i, j):
        """
        Calculate the shape factor between two faces.
        Fij ~ cos(phi_i) cos(phi_j) * Aj / (pi * r^2)
        """
        if i == j:
            return 0.0
        else:
            if self._is_object_between(i, j):
                return 0.0
            else: 
                theta_j = self._get_angle_between_faces(i, j)
                theta_i = self._get_angle_between_faces(j, i)
                if theta_j <= np.pi/2:
                    return 0.0
                else:
                    r_2 = np.sum(np.power(self._t[j].centroid - self._t[i].centroid, 2))
                    return np.cos(theta_i) * np.cos(theta_j) * self._t[j].area / (np.pi * r_2)

    def solve(self):
        """
        Solve the radiosity linear system.
        A @ B = E
        """
        for c in range(self._NUM_COLORS):
            self.B[:, c] = np.linalg.solve(self.A[:, :, c], self.E[:, c])
        file_B = open("./utils/numpy_files/B.npy", 'wb') 
        np.save(file_B, self.B)


   