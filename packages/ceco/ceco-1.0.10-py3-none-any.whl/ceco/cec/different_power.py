from ceco.benchmark import Benchmark
import numpy as np


class Different_power(Benchmark):
    """
    A class representing the Different Power benchmark function, used for optimization problems.

    The Different Power function is a unimodal, non-separable, and scalable function.
    It is defined as:
    f(X) = sqrt{sum_{i=1}^{D} left| x_i right|^{2 + 4 frac{i-1}{D-1}}}
    where X = [x_1, x_2, ..., x_D] is the input vector of dimension ( D ).

    This class inherits from the `Benchmark` class and implements the `evaluate` method
    to compute the value of the Discus function after applying shift and rotation
    transformations to the input vector.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Different_power class with a rotation matrix, a shift vector, and a bias term.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)
        if self.dimension > 1:
            self.exponents = 2 + 4 * \
                (np.arange(self.dimension) / (self.dimension - 1))
        else:
            self.exponents = None

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Different power function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Different power function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)
        if self.dimension == 1:
            return np.abs(shifted_rotated_vector[0]) + self.f_bias

        # Vectorized computation
        total_sum = np.sum(np.abs(shifted_rotated_vector) ** self.exponents)
        total_sum = np.sqrt(total_sum) + self.f_bias

        return total_sum
