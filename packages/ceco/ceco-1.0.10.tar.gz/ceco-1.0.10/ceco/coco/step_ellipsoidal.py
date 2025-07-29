import numpy as np
from ceco.benchmark import Benchmark


class Step_ellipsoidal(Benchmark):
    """
    A class representing the Step ellipsoidal function, which is a benchmark function
    for optimization.

    The Step ellipsoidal function is defined as:

        f(x) = 0.1 * max(|x_1| / 10^4, sum_{i=1}^{D} 10^(2 * (i-1) / (D-1)) * x_i^2)

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Step ellipsoidal function with a given dimension.

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
            self.weight = np.array([1.0])
        else:
            exponents = 2 * (np.arange(dimension) - 1) / (dimension - 1)
            self.weight = 10 ** exponents

        self.f_opt = self.raw(self.x_opt)

        # Precompute rotation matrices
        self.R = self.gram_schmidt(self.generate_random_matrix(dimension).T)
        self.Q = self.gram_schmidt(self.generate_random_matrix(dimension).T)

        # Precompute diagonal scaling matrix Λ^10
        self.diag_matrix = self.create_diagonal_matrix(10)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Step ellipsoidal function at a given input vector without any shift.

        The function is calculated as:
            f(x) = 0.1 * max(|x_1| / 10^4, sum_{i=1}^{D} 10^(2 * (i-1) / (D-1)) * x_i^2)

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

        term1 = np.abs(x[0]) / 1e4
        term2 = np.sum(self.weight * x ** 2)
        return 0.1 * max(term1, term2)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Step ellipsoidal function at a given input vector.

        The function is calculated as:
            f(x) = 0.1 * max(|z_hat_1| / 10^4, sum_{i=1}^{D} 10^(2 * (i-1) / (D-1)) * z_i^2) + f_pen(x) + f_opt

        where:
          z_hat = Λ^10 * R * (x - x_opt)
          z_tilde is obtained by applying a rounding transformation to z_hat
          z = Q * z_tilde

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Step ellipsoidal function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        diff = input_vector - self.x_opt
        z_hat = self.diag_matrix @ (self.R @ diff)

        abs_z_hat = np.abs(z_hat)
        z_tilde = np.where(
            abs_z_hat > 0.5,
            np.floor(0.5 + z_hat),
            np.floor(0.5 + 10 * z_hat) / 10
        )
        z = self.Q @ z_tilde
        term1 = np.abs(z_hat[0]) / 1e4
        term2 = np.sum(self.weight * z ** 2)

        result = 0.1 * max(term1, term2) + \
            self.f_pen(input_vector) + self.f_opt

        return result
