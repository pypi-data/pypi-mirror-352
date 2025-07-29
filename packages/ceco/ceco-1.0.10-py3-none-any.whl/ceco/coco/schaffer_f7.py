import numpy as np
from ceco.benchmark import Benchmark


class Schaffer_f7(Benchmark):
    """
    A class representing the Schaffer f7 function, which is a benchmark function
    for optimization.

    The Schaffer f7 function is defined as:

        f(x) = ( frac{1}{D-1}sum_{i=1}^{D-1}( sqrt{x_i}+sqrt{x_i}sin^2( 50x_i^{0.2} ) ) )^2 for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
        ill_conditioned (bool): If `True`,
    """

    def __init__(self, dimension: int, ill_conditioned: bool = False) -> None:
        """
        Initializes the Schaffer f7 function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            high_conditioning (bool, optional): If `True`, . Defaults to `False`.

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        if dimension == 1:
            raise ValueError("Dimension must be greater than 1")
        super().__init__(dimension)
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(0, 5, dimension)

        self.f_opt = self._schaffer_raw(self.x_opt[:-1])

        if not isinstance(ill_conditioned, bool):
            raise ValueError("ill_conditioned must be a boolean")
        self.ill_conditioned = ill_conditioned
        self.diagonal_matrix = self.create_diagonal_matrix(
            1000) if self.ill_conditioned else self.create_diagonal_matrix(10)
        self.R = self.generate_random_matrix(dimension)
        self.R = self.gram_schmidt(self.R)
        self.Q = self.generate_random_matrix(dimension)
        self.Q = self.gram_schmidt(self.Q)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Schaffer f7 function at a given input vector without any shift.

        The function is calculated as:
            f(x) = ( frac{1}{D-1}sum_{i=1}^{D-1}( sqrt{x_i}+sqrt{x_i}sin^2( 50x_i^{0.2} ) ) )^2 for i in [1, D]

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

        if np.any(x[:-1] < 0):
            raise ValueError(
                "All elements in input vector must be non-negative")
        return self._schaffer_raw(x[:-1])

    def _schaffer_raw(self, s: np.ndarray) -> float:
        """
        Evaluates the Schaffer f7 function at a given input vector after transformation.

        The function is calculated as:
            f(x) = ( frac{1}{D-1}sum_{i=1}^{D-1}( sqrt{x_i}+sqrt{x_i}sin^2( 50x_i^{0.2} ) ) )^2 for i in [1, D]

        Parameters:
            s (np.ndarray): A vector of real numbers representing a candidate solution.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if np.any(s < 0):
            raise ValueError(
                "all element in Input vector must be non-negative after transformation")
        sqrt_s = np.sqrt(s)
        s_pow = s ** 0.2
        sin_term = np.sin(50 * s_pow)
        inner_term = sqrt_s + sqrt_s * np.square(sin_term)
        total_sum = np.sum(inner_term)
        result = (total_sum / (self.dimension - 1)) ** 2

        return result

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Schaffer f7 function at a given input vector.

        The function is calculated as:
            f(x) = ( frac{1}{D-1}sum_{i=1}^{D-1}( sqrt{x_i}+sqrt{x_i}sin^2( 50x_i^{0.2} ) ) )^2 + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Schaffer f7 function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
            ValueError: If the input vector after transform is zero or negative.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        # Shift the input vector
        z = self.diagonal_matrix @ self.Q @ self.T_asy_beta(
            0.5, self.R @ (input_vector - self.x_opt))

        s = np.sqrt(np.square(z[:-1]) + np.square(z[1:]))

        if np.any(s < 0):
            raise ValueError(
                "Elements in transformed vector must be non-negative")

        schaffer_value = self._schaffer_raw(s)

        # Compute the raw Schaffer f7 function value
        result = schaffer_value + 10 * self.f_pen(input_vector) + self.f_opt

        return result
