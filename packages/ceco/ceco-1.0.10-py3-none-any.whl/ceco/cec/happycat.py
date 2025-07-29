from ceco.benchmark import Benchmark
import numpy as np


class Happycat(Benchmark):
    """
    A class representing the Happycat benchmark function, used for optimization problems.

    The Happycat function is a highly multimodal, non-separable, and scalable function.
    It is defined as:
    f(X)=\| sum_{i=1}^{D}x_i^2-D \|^{1/4}+(0.5 sum_{i=1}^{D}x_i^2+ sum_{i=1}^{D}x_i)/D+0.5
    where X = [x_1, x_2, ..., x_D] is the input vector of dimension ( D ).

    This class inherits from the `Benchmark` class and implements the `evaluate` method to compute the value of the Discus function after applying shift and rotation transformations to the input vector.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Happycat class with a rotation matrix, a shift vector, and a bias term.

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
        Evaluates the Happycat function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Happycat function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        sum_x_squared = np.sum(shifted_rotated_vector ** 2)
        sum_x = np.sum(shifted_rotated_vector)

        term1 = np.abs(sum_x_squared - self.dimension) ** (1/4)
        term2 = (0.5 * sum_x_squared + sum_x) / self.dimension

        result = term1 + term2 + 0.5 + self.f_bias

        return result
