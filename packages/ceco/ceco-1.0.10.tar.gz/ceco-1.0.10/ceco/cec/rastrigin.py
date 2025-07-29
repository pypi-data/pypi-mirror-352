from ceco.benchmark import Benchmark
import numpy as np


class Rastrigin(Benchmark):
    """
    A class representing the Rastrigin function, which is a benchmark function
    for optimization.

    The Rastrigin function is defined as:
    F(X) = sum_{i=1}^{D} (x_i^2 - 10 * cos(2 * pi * x_i) + 10)

    The class inherits from the `Benchmark` class and applies rotation and shift
    transformations to the input vector before evaluating the function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Rastrigin class with a rotation matrix and a shift vector.

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
        Evaluates the Rastrigin function at a given input vector after applying
        rotation and shift transformations.

        The function first applies the rotation matrix and shift vector to the input vector.
        Then, it computes the Rastrigin function:
        F(X) = sum_{i=1}^{D} (x_i^2 - 10 * cos(2 * pi * x_i) + 10).

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Rastrigin function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)
        # Compute the Rastrigin function
        total_sum = np.sum(shifted_rotated_vector ** 2 - 10 *
                           np.cos(2 * np.pi * shifted_rotated_vector) + 10) + self.f_bias

        return total_sum
