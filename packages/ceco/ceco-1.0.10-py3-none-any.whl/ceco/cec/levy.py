from ceco.benchmark import Benchmark
import numpy as np


class Levy(Benchmark):
    """
    A class representing the Levy benchmark function, used for optimization problems.

    It is defined as:
    f(X)=sin^2(pi w_1)+ sum_{i=1}^{D-1}(w_i-1)^2[ 1+10 sin^2(pi w_i+1) ]+(w_D-1)^2[ 1+ sin^2(2 pi w_D) ]

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
        Initializes the Levy class with a rotation matrix, a shift vector, and a bias term.

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
        Evaluates the Levy function for the given input vector after applying shift and rotation transformations.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Levy function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        w = 1 + (shifted_rotated_vector - 1) / 4.0

        term1 = np.sin(np.pi * w[0]) ** 2

        sum_term = np.sum((w[:-1] - 1) ** 2 * (1 + 10 *
                          np.sin(np.pi * w[:-1] + 1) ** 2))
        term2 = (w[-1] - 1) ** 2 * \
            (1 + np.sin(2 * np.pi * w[-1]) ** 2)
        result = term1 + sum_term + term2 + self.f_bias
        return result
