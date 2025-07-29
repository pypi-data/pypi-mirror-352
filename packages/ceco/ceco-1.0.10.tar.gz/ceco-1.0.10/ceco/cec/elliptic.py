from ceco.benchmark import Benchmark
import numpy as np


class Elliptic(Benchmark):
    """
    A class representing the Elliptic function, which is a benchmark function
    for optimization.

    The Elliptic function is commonly used to test optimization algorithms due to its
    highly anisotropic and ill-conditioned nature. The function is defined as:
    F(X) = sum_{i=1 to D} (10^6)^((i-1)/(D-1)) * (x_i)^2,
    where D is the dimensionality of the problem.

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
        Initializes the Elliptic class with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)

        if self.dimension > 1:
            self.scaling_factors = (
                10**6) ** (np.arange(self.dimension) / (self.dimension - 1))
        else:
            self.scaling_factors = None

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Elliptic function at a given input vector after applying
        rotation and shift transformations.

        The function first applies the rotation matrix and shift vector to the input vector.
        Then, it computes the Elliptic function:
        F(X) = sum_{i=1 to D} (10^6)^((i-1)/(D-1)) * (x_i)^2.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Elliptic function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Calculate the Elliptic function
        if self.dimension == 1:
            return ((10 ** 6) ** 2) * (shifted_rotated_vector[0] ** 2) + self.f_bias

        # Vectorized computation
        total_sum = np.sum(self.scaling_factors *
                           (shifted_rotated_vector ** 2))

        return total_sum + self.f_bias
