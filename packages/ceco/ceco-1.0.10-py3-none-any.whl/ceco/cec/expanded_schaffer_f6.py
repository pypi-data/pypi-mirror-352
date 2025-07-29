from ceco.benchmark import Benchmark
import numpy as np


class Expanded_schaffer_f6(Benchmark):
    """
    A class representing the Expanded Schaffer F6 function, which is a benchmark function for optimization problems.

    The Expanded Schaffer F6 function is defined as:

    F(X) = sum_{i=1}^{D-1} SchafferBase(x_i, x_{i+1}) + SchafferBase(x_D, x_1)

    where:
    - SchafferBase(x, y) = 0.5 + (sin(sqrt(x^2 + y^2))^2 - 0.5) / (1 + 0.001 * (x^2 + y^2))^2
    - X = (x_1, x_2, ..., x_D) is a D-dimensional input vector.

    This class inherits from the Benchmark class and applies rotation and shift transformations to the input vector before evaluating the function.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Expanded Schaffer F6 class with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)

    def schaffer_base(self, x: float, y: float) -> float:
        """
        Computes the Schaffer base function for two variables.

        The Schaffer base function is defined as:

        SchafferBase(x, y) = 0.5 + (sin(sqrt(x^2 + y^2))^2 - 0.5) / (1 + 0.001 * (x^2 + y^2))^2

        Parameters:
            x (float): The first variable.
            y (float): The second variable.

        Returns:
            float: The result of the Schaffer base function.
        """
        term = x**2 + y**2
        numerator = np.sin(np.sqrt(term)) ** 2 - 0.5
        denominator = (1 + 0.001 * term) ** 2
        return 0.5 + numerator / denominator

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Expanded Schaffer F6 function at a given input vector after applying rotation and shift transformations.

        The evaluation process involves the following steps:
        1. Apply the rotation matrix to the input vector to obtain the rotated vector.
        2. Apply the shift vector to the rotated vector to obtain the shifted vector.
        3. Calculate the Expanded Schaffer F6 function using the shifted vector.

        The function is computed as:

        F(X) = sum_{i=1}^{D-1} SchafferBase(x_i, x_{i+1}) + SchafferBase(x_D, x_1)

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Expanded Schaffer F6 function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        total_sum = 0.0

        # Compute the sum of F(x_i, x_{i+1}) for i = 1 to D-1
        for i in range(self.dimension - 1):
            total_sum += self.schaffer_base(
                shifted_rotated_vector[i], shifted_rotated_vector[i + 1])

        # Add the term F(x_D, x_1)
        total_sum += self.schaffer_base(
            shifted_rotated_vector[-1], shifted_rotated_vector[0])

        return total_sum + self.f_bias
