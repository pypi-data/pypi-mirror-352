from ceco.benchmark import Benchmark
import numpy as np


class Shubert(Benchmark):
    """
    A class representing the Shubert benchmark function, used for optimization problems.

    The Shubert function is a multimodal, non-separable, and scalable function.
    It is defined as:
    f(X)=- prod_{i=1}^{D} sum_{j=1}^{5}j cos\[ (j+1)x_i+j ]
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
        Initializes the Shubert class with a rotation matrix, a shift vector, and a bias term.

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
        Evaluates the Shubert function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Shubert function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        j_values = np.arange(1, 6)
        cos_terms = np.cos(
            (j_values[:, np.newaxis] + 1) * shifted_rotated_vector + j_values[:, np.newaxis])
        sum_terms = np.sum(j_values[:, np.newaxis] * cos_terms, axis=0)
        product = np.prod(sum_terms)
        return -product + self.f_bias
