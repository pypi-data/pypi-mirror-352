import numpy as np
from ceco.benchmark import Benchmark


class Linear_slope(Benchmark):
    """
    A class representing the Linear slope function, which is a benchmark function
    for optimization.

    The Linear slope function is defined as:

        f(x) = sum_{i=1}^{D}5| s_i |-s_iz_i

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Linear slope function with a given dimension.

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
        if dimension == 1:
            self.s = np.sign(self.x_opt) * 1.0
        else:
            self.s = np.sign(self.x_opt) * \
                (10 ** (np.arange(dimension)/(dimension - 1)))

        self.f_opt = self.raw(self.x_opt)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Linear slope function at a given input vector without any shift.

        The function is calculated as:
            f(x) = sum_{i=1}^{D}5| s_i |-s_iz_i

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

        result = np.sum(5 * np.abs(self.s) - self.s * x)
        return result

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Linear slope function at a given input vector.

        The function is calculated as:
            f(x) = sum_{i=1}^{D}5| s_i |-s_iz_i+ f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Linear slope function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        z = np.where((input_vector * self.x_opt) <
                     5 ** 2, input_vector, self.x_opt)
        result = self.raw(z) + self.f_opt

        return result
