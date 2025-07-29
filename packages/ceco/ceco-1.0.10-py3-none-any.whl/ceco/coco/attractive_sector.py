import numpy as np
from ceco.benchmark import Benchmark


class Attractive_sector(Benchmark):
    """
    A class representing the Attractive sector function, which is a benchmark function
    for optimization.

    The Attractive sector function is defined as:

        f(x) = T_{text{osz}}( sum_{i=1}^{D}( s_iz_i )^2 )^{0.9}

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Attractive sector function with a given dimension.

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

        # Precompute rotation matrices
        self.R = self.gram_schmidt(self.generate_random_matrix(dimension).T)
        self.Q = self.gram_schmidt(self.generate_random_matrix(dimension).T)

        self.diag_matrix = self.create_diagonal_matrix(10)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Attractive sector function at a given input vector without any shift.

        The function is calculated as:
            f(x) = T_{text{osz}}( sum_{i=1}^{D}( s_iz_i )^2 )^{0.9}

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

        s = np.where((x * self.x_opt), 10 ** 2, 1)

        result = np.sum((s * x) ** 2)
        return result ** 0.9

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Attractive sector function at a given input vector.

        The function is calculated as:
            f(x) = T_{text{osz}}( sum_{i=1}^{D}( s_iz_i )^2 )^{0.9}+ f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Attractive sector function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        z = self.Q @ self.diag_matrix @ self.R @ (input_vector - self.x_opt)
        result = self.T_osz(self.raw(z)) + self.f_opt

        return result
