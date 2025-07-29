from ceco.benchmark import Benchmark
import numpy as np


class Sphere(Benchmark):
    """
    A class representing the Sphere function, which is a benchmark function
    for optimization.

    Inherits from the Benchmark class and applies rotation and shift to the
    standard sphere function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Sphere class with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the rotated and shifted sphere function at a given input vector.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the sphere function after applying rotation
            and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Calculate the sum of squares
        result = np.sum(shifted_rotated_vector ** 2)

        return result + self.f_bias
