from ceco.benchmark import Benchmark
import numpy as np


class Ackley(Benchmark):
    """
    A class representing the Ackley function, which is a benchmark function for optimization.

    The Ackley function is commonly used to test optimization algorithms due to its complex and multi-modal nature. The function is defined as:

    F(X) = -20 * exp(-0.2 * sqrt((1/D) * sum_{i=1}^D x_i^2)) - exp((1/D) * sum_{i=1}^D cos(2 * pi * x_i)) + 20 + e,

    where D is the dimensionality of the problem, and e is Euler's number (~2.71828).

    The class inherits from the `Benchmark` class and applies rotation and shift transformations to the input vector before evaluating the function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Ackley class with a rotation matrix and a shift vector.

        Ensures that the rotation matrix and shift vector have the same length. If their lengths do not match, a ValueError is raised.

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
        Evaluates the Ackley function at a given input vector after applying rotation and shift transformations.

        The function first applies the rotation matrix and shift vector to the input vector. Then, it computes the Ackley function:
        F(X) = -20 * exp(-0.2 * sqrt((1/D) * sum_{i=1}^D x_i^2)) - exp((1/D) * sum_{i=1}^D cos(2 * pi * x_i)) + 20 + e.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Ackley function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        sum_term1 = np.sum(shifted_rotated_vector ** 2)
        sum_term2 = np.sum(np.cos(2 * np.pi * shifted_rotated_vector))

        term1 = np.exp(-0.2 * np.sqrt(sum_term1 / self.dimension))
        term2 = -np.exp(sum_term2 / self.dimension)
        result = -20 * term1 + term2 + 20 + np.e + self.f_bias

        return result
