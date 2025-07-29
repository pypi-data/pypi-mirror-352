import numpy as np
from ceco.benchmark import Benchmark


class Sharp_ridge(Benchmark):
    """
    Implements the Sharp ridge function, a common benchmark function for optimization problems.

    The Sharp ridge function is defined as:

        f(x) = z_1^2+100\sqrt{\sum_{i=2}^{D}z_i^2} for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Sharp ridge function with a given dimension.

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

        self.R = self.gram_schmidt(self.generate_random_matrix(dimension).T)
        self.Q = self.gram_schmidt(self.generate_random_matrix(dimension).T)

        self.diag_matrix = self.create_diagonal_matrix(10)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Sharp ridge function at a given input vector without any shift.

        The function is calculated as:

            f(x) = z_1^2+100\sqrt{\sum_{i=2}^{D}z_i^2} for i in [1, D]

        Parameters:
            x (np.ndarray): A vector of real numbers representing a candidate solution.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if len(x) != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")
        first_term = x[0] ** 2
        sum_term = np.linalg.norm(x[1:])
        return first_term + 100 * sum_term

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Sharp ridge function at a given input vector.

        The function is calculated as:

            f(x) = z_1^2+100\sqrt{\sum_{i=2}^{D}z_i^2} + frac{10}{D}f_pen(x) + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Sharp ridge function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if len(input_vector) != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")
        z = self.Q @ self.diag_matrix @ self.R @ (
            input_vector - self.x_opt)
        result = self.raw(z) + self.f_opt

        return result
