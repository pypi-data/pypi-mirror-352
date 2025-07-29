import numpy as np
from ceco.benchmark import Benchmark


class Different_power(Benchmark):
    """
    A class representing the Different power function, which is a benchmark function
    for optimization.

    The Different power function is defined as:

        f(x) = sqrt{sum_{i=1}^{D} left| x_i right|^{2 + 4 frac{i-1}{D-1}}} for i in [1, D]

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Different power function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            high_conditioning (bool, optional): If `True`, applies a Gram-Schmidt transformation to increase problem conditioning. Defaults to `False`.

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        super().__init__(dimension)
        if self.dimension > 1:
            self.exponents = 2 + 4 * \
                (np.arange(self.dimension) / (self.dimension - 1))
        else:
            self.exponents = np.array([2.0])
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(-5, 5, dimension)

        self.f_opt = self.raw(self.x_opt)

        self.R = self.generate_random_matrix(dimension)
        self.R = self.gram_schmidt(self.R)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Different power function at a given input vector without any shift.

        The function is calculated as:
            f(x) = sqrt{sum_{i=1}^{D} left| x_i right|^{2 + 4 frac{i-1}{D-1}}} for i in [1, D]

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

        abs_x = np.abs(x)
        total_sum = np.sum(abs_x ** self.exponents)
        total_sum = np.sqrt(total_sum)

        return total_sum

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Different power function at a given input vector.

        The function is calculated as:
            f(x) = sqrt{sum_{i=1}^{D} left| x_i right|^{2 + 4 frac{i-1}{D-1}}} + f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Different power function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        # Shift the input vector
        z = np.matmul(self.R, (input_vector - self.x_opt))

        # Compute the raw Different power function value
        result = self.raw(z) + self.f_opt

        return result
