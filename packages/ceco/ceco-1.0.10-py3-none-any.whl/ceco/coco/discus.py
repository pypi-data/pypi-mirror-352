import numpy as np
from ceco.benchmark import Benchmark


class Discus(Benchmark):
    """
    A class representing the Discus function, which is a benchmark function
    for optimization.

    The Discus function is defined as:

        f(x) = 10^6 * x_1^2 + sum_{i=2}^{D} x_i^2 for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Discus function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        super().__init__(dimension)
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(-5, 5, dimension)

        self.f_opt = self.raw(self.x_opt)

        self.R = self.generate_random_matrix(dimension)
        self.R = self.gram_schmidt(self.R)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Discus function at a given input vector without any shift.

        The function is calculated as:
            f(x) = 10^6 * x_1^2 + sum_{i=2}^{D} x_i^2 for i in [1, D]

        Parameters:
            x (np.ndarray): A vector of real numbers representing a candidate solution.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if x.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        sum_term = np.sum(x[1:] ** 2)

        total_sum = (10 ** 6) * x[0] ** 2 + sum_term

        return total_sum

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Discus function at a given input vector.

        The function is calculated as:
            f(x) = 10^6 * x_1^2 + sum_{i=2}^{D} x_i^2 + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Discus function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        # Shift the input vector
        z = self.T_osz(np.matmul(self.R, (input_vector - self.x_opt)))

        # Compute the raw Discus function value
        result = self.raw(z) + self.f_opt

        return result
