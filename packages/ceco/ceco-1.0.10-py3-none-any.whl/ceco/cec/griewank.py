from ceco.benchmark import Benchmark
import numpy as np


class Griewank(Benchmark):
    """
    A class representing the Griewank function, a commonly used benchmark function
    in optimization problems. It inherits from the Benchmark class and applies
    rotation and shift transformations before evaluation.

    The Griewank function is defined as:

        f(x) = (1/4000) * sum(x_i^2) - prod(cos(x_i / sqrt(i+1))) + 1

    where:
        - The first term represents the sum of squared components divided by 4000.
        - The second term is the product of cosine terms applied to each component.
        - The final term is a constant used to adjust the function's range.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Griewank function with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)
        self.i_value = np.arange(1, self.dimension + 1)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the rotated and shifted Griewank function at a given input vector.

        The function first applies a rotation transformation followed by a shift
        transformation to the input vector before computing the Griewank function.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The computed Griewank function value after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        sum_term = np.sum(shifted_rotated_vector ** 2 / 4000)

        product_term = np.prod(
            np.cos(shifted_rotated_vector/np.sqrt(self.i_value)))

        result = sum_term - product_term + 1 + self.f_bias
        return result
