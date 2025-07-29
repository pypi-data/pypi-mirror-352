from ceco.benchmark import Benchmark
import numpy as np


class Weierstrass(Benchmark):
    """
    A class representing the Weierstrass function, a continuous but nowhere differentiable function 
    used as a benchmark in optimization problems.

    Inherits from the Benchmark class and applies rotation and shift transformations to the 
    standard Weierstrass function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        a (float): The decay factor, default is 0.5.
        b (float): The frequency factor, default is 3.
        k_max (int): The maximum number of summation terms, default is 20.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Weierstrass class with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)
        self.a = 0.5
        self.b = 3
        self.k_max = 20

        self.k_values = np.arange(self.k_max + 1)  # k = 0, 1, ..., k_max
        self.a_pow_k = self.a ** self.k_values  # a^k for all k
        self.b_pow_k = self.b ** self.k_values  # b^k for all k

        # Compute the second part of the function
        self.second_sum = np.sum(
            self.a_pow_k * np.cos(2 * np.pi * self.b_pow_k * 0.5)
        )

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the rotated and shifted Weierstrass function at a given input vector.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Weierstrass function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Compute the first part of the function
        inner_sum = np.sum(
            self.a_pow_k[:, np.newaxis] *
            np.cos(2 * np.pi * self.b_pow_k[:, np.newaxis]
                   * (shifted_rotated_vector + 0.5)),
            axis=0
        )
        total_sum = np.sum(inner_sum)

        # Final result
        result = total_sum - self.dimension * self.second_sum + self.f_bias
        return result
