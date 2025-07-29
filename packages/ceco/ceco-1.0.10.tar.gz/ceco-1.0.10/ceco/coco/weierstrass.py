import numpy as np
from ceco.benchmark import Benchmark


class Weierstrass(Benchmark):
    """
    Implements the Weierstrass function, a common benchmark function for optimization problems.

    The Weierstrass function is defined as:

        f(x) = 10( frac{1}{D}\sum_{i=1}^{D}\sum_{k=0}^{11}1/2^k\cos( 2\pi 3^k( z_i + 1/2 ) ) -f_0 )^3 for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Weierstrass function with a given dimension.

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

        k_values = np.arange(12)
        self.three_pow_k = 3 ** k_values
        self.two_pow_k = 2 ** k_values
        self.f0 = np.sum(np.cos(np.pi * self.three_pow_k) / self.two_pow_k)

        self.f_opt = self.raw(self.x_opt)

        self.R = self.gram_schmidt(self.generate_random_matrix(dimension).T)
        self.Q = self.gram_schmidt(self.generate_random_matrix(dimension).T)

        self.diag_matrix = self.create_diagonal_matrix(1/100)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Weierstrass function at a given input vector without any shift.

        The function is calculated as:

            f(x) = 10( frac{1}{D}\sum_{i=1}^{D}\sum_{k=0}^{11}1/2^k\cos( 2\pi 3^k( z_i + 1/2 ) ) -f_0 )^3 for i in [1, D]

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
        x_expanded = x[:, np.newaxis]
        k_term = np.cos(2 * np.pi * self.three_pow_k *
                        (x_expanded + 0.5)) / self.two_pow_k
        sum_over_k = np.sum(k_term, axis=1)
        avg_sum = np.mean(sum_over_k)
        return 10 * (avg_sum - self.f0) ** 3

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Weierstrass function at a given input vector.

        The function is calculated as:

            f(x) = 10( frac{1}{D}\sum_{i=1}^{D}\sum_{k=0}^{11}1/2^k\cos( 2\pi 3^k( z_i + 1/2 ) ) -f_0 )^3 + frac{10}{D}f_pen(x) + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Weierstrass function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if len(input_vector) != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")
        z = self.R @ self.diag_matrix @ self.Q @ self.T_osz(
            self.R @ (input_vector - self.x_opt))
        result = self.raw(z) + (10/self.dimension) * \
            self.f_pen(input_vector) + self.f_opt

        return result
