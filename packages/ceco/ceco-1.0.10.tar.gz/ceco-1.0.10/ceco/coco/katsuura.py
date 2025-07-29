import numpy as np
from ceco.benchmark import Benchmark


class Katsuura(Benchmark):
    """
    A class representing the Katsuura function, which is a benchmark function
    for optimization.

    The Katsuura function is defined as:

        f(x) = frac{10}{D^2} prod_{i=1}^D ( 1 + i sum_{j=1}^{32} frac{\|2^j x_i - round(2^j x_i)\|}{2^j} )^{frac{10}{D^{1.2}}} - frac{10}{D^2} for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Katsuura function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            high_conditioning (bool, optional): If `True`, applies a Gram-Schmidt transformation to increase problem conditioning. Defaults to `False`.

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        super().__init__(dimension)
        self.powers_of_two = 2 ** np.arange(1, 33)
        self.inverse_powers = 1 / self.powers_of_two
        self.exponent = 10 / (self.dimension ** 1.2)
        self.scale_factor = 10 / (self.dimension ** 2)
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(-5, 5, dimension)

        self.f_opt = self.raw(self.x_opt)

        self.R = self.generate_random_matrix(dimension)
        self.R = self.gram_schmidt(self.R)
        self.Q = self.generate_random_matrix(dimension)
        self.Q = self.gram_schmidt(self.Q)
        self.diagonal_matrix = self.create_diagonal_matrix(100)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Katsuura function at a given input vector without any shift.

        The function is calculated as:
            f(x) = frac{10}{D^2} prod_{i=1}^D ( 1 + i sum_{j=1}^{32} frac{\|2^j x_i - round(2^j x_i)\|}{2^j} )^{frac{10}{D^{1.2}}} - frac{10}{D^2} for i in [1, D]

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

        fractional_part = np.abs(
            self.powers_of_two[:, None] * x -
            np.round(self.powers_of_two[:, None] * x)
        )

        # Compute sum term using vectorized operations
        sum_terms = np.sum(fractional_part *
                           self.inverse_powers[:, None], axis=0)

        # Compute product term efficiently
        indices = np.arange(1, self.dimension + 1)
        prod_terms = (1 + indices * sum_terms) ** self.exponent

        product = np.prod(prod_terms)

        return self.scale_factor * product - self.scale_factor

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Katsuura function at a given input vector.

        The function is calculated as:
            f(x) = frac{10}{D^2} prod_{i=1}^D ( 1 + i sum_{j=1}^{32} frac{\|2^j x_i - round(2^j x_i)\|}{2^j} )^{frac{10}{D^{1.2}}} - frac{10}{D^2} + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Katsuura function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        # Shift the input vector
        z = input_vector - self.x_opt
        z = self.Q @ self.diagonal_matrix @ self.R @ z

        # Compute the raw Katsuura function value
        result = self.raw(z) + self.f_pen(input_vector) + self.f_opt

        return result
