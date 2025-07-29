from ceco.benchmark import Benchmark
import numpy as np


class Katsuura(Benchmark):
    """
    A class representing the Katsuura benchmark function, used for optimization problems.

    The Katsuura function is a highly multimodal, non-separable, and scalable function.
    It is defined as:
    f(X) = frac{10}{D^2} prod_{i=1}^D ( 1 + i sum_{j=1}^{32} frac{\|2^j x_i - round(2^j x_i)\|}{2^j} )^{frac{10}{D^{1.2}}} - frac{10}{D^2}
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
        Initializes the Katsuura class with a rotation matrix, a shift vector, and a bias term.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)
        self.j_values = np.arange(1, 33)
        self.powers_of_two = 2 ** self.j_values
        self.exponent = 10 / (self.dimension ** 1.2)
        self.scale_factor = 10 / (self.dimension ** 2)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Katsuura function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Katsuura function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        powers_of_2 = 2 ** np.arange(1, 33)

        # Compute sum term using vectorized operations
        sum_terms = np.sum(
            np.abs(powers_of_2[:, None] * shifted_rotated_vector - np.round(
                powers_of_2[:, None] * shifted_rotated_vector)) / powers_of_2[:, None],
            axis=0
        )

        # Compute product term efficiently
        indices = np.arange(1, self.dimension + 1)
        product = np.prod((1 + indices * sum_terms) **
                          (10 / (self.dimension ** 1.2)))

        # Compute final result
        result = (10 / (self.dimension ** 2)) * product - \
            (10 / (self.dimension ** 2)) + self.f_bias

        return result
