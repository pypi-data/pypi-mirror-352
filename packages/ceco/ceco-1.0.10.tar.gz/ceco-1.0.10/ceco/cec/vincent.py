from ceco.benchmark import Benchmark
import numpy as np


class Vincent(Benchmark):
    """
    A class representing the Vincent benchmark function, used for optimization problems.

    The Vincent function is defined as:

    F(X) = (1/D) * sum_{i=1}^{D} sin(10 * log(x_i))
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
        Initializes the Vincent class with a rotation matrix, a shift vector, and a bias term.

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
        Evaluates the Vincent function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Vincent function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Check if all elements are greater than 0
        if np.any(shifted_rotated_vector <= 0):
            raise ValueError(
                "All elements in input_vector must be greater than 0 after shift and rotation")

        # Compute the Vincent function using vectorized operations
        total_sum = np.sum(np.sin(10 * np.log(shifted_rotated_vector)))

        return 1 / self.dimension * total_sum + self.f_bias
