from ceco.benchmark import Benchmark
import numpy as np


class Ellipsoid(Benchmark):
    """
    A class representing the Ellipsoid function, which is a benchmark function
    for optimization.

    The Ellipsoid function is defined as:

    F(X) = sum_{i=1}^{D} i * (x_i)^2

    where:
    - D is the dimension of the input vector.
    - x = (x1, x2, ..., xD) is a D-dimensional row vector (i.e., a 1xD matrix).
    - The function is characterized by its elongated shape, which can make optimization algorithms struggle to find the global minimum.

    This class inherits from the Benchmark class and applies rotation and shift transformations to the input vector before evaluating the function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Ellipsoid class with a rotation matrix and a shift vector.

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
        Evaluates the Ellipsoid function at a given input vector after applying
        rotation and shift transformations.

        The evaluation process involves the following steps:
        1. Apply the rotation matrix to the input vector to obtain the rotated vector.
        2. Apply the shift vector to the rotated vector to obtain the shifted vector.
        3. Calculate the Ellipsoid function using the shifted vector.

        The Ellipsoid function is computed as follows:

        F(X) = sum_{i=1}^{D} i * (x_i - shift_i)^2

        where:
        - x_i is the i-th element of the shifted vector.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Ellipsoid function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Calculate the Ellipsoid function
        i_value = np.arange(1, self.dimension + 1, dtype=np.float64)
        result = np.sum(i_value * (shifted_rotated_vector ** 2))

        return result + self.f_bias
