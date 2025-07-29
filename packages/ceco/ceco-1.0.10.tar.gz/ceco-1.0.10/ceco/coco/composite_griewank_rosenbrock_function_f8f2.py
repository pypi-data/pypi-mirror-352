import numpy as np
from ceco.benchmark import Benchmark


class Composite_griewank_rosenbrock_function_f8f2(Benchmark):
    """
    A class representing the Composite griewank-rosenbrock function f8f2 function, which is a benchmark function
    for optimization.

    The Composite griewank-rosenbrock function f8f2 function is defined as:

        f(x) = \frac{10}{D-1}\sum_{i=1}^{D-1}\left( \frac{x_i}{4000}-\cos\left( x_i \right) \right)+10

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Composite griewank-rosenbrock function f8f2 function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        if dimension == 1:
            raise ValueError("Dimension must be greater than 1")
        super().__init__(dimension)
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(-5, 5, dimension)

        self.f_opt = self.raw(self.x_opt)

        self.alpha = max(1, np.sqrt(self.dimension)/8)

        # Precompute rotation matrices
        self.R = self.gram_schmidt(self.generate_random_matrix(dimension).T)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Composite griewank-rosenbrock function f8f2 function at a given input vector without any shift.

        The function is calculated as:
            f(x) = \frac{10}{D-1}\sum_{i=1}^{D-1}\left( \frac{x_i}{4000}-\cos\left( x_i \right) \right)+10

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

        summation = np.sum((x[:-1]/4000)-np.cos(x[:-1]))
        return (10 / (self.dimension - 1)) * summation + 10

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Composite griewank-rosenbrock function f8f2 function at a given input vector.

        The function is calculated as:
            f(x) = frac{10}{D-1}\sum_{i=1}^{D-1}\left( frac{x_i}{4000}-\cos\left( x_i \right) \right)+10+ f_opt

        where:
          z_hat = Λ^10 * R * (x - x_opt)
          z_tilde is obtained by applying a rounding transformation to z_hat
          z = Q * z_tilde

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Composite griewank-rosenbrock function f8f2 function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        z = self.alpha * self.R @ input_vector + 0.5
        z_i = z[:-1]
        z_next = z[1:]
        s = 100 * (z_i ** 2 - z_next) ** 2 + (z_i - 1) ** 2
        summation = np.sum((s/4000)-np.cos(s))
        raw_result = (10 / (self.dimension - 1)) * summation + 10
        result = raw_result + self.f_opt

        return result
