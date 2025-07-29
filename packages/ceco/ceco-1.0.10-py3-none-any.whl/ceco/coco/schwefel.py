import numpy as np
from ceco.benchmark import Benchmark


class Schwefel(Benchmark):
    """
    A class representing the Schwefel function, which is a benchmark function for optimization.

    The Schwefel function is defined as:

        f(X)= -frac{1}{100D}sum_{i=1}^{D}x_i sin(sqrt{| x_i |}) + 4.189828872724339 + 100f_{pen}(z/100) + f_{opt}
        where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
        sign_vector (np.ndarray): Vector of random signs (±1) used in transformations.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Schwefel function with a given dimension.

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
        # Generate random sign vector (±1) to be used in transformations
        self.sign_vector = np.random.choice([-1, 1], dimension)
        # Generate the true optimal point as defined in the formula
        self.true_x_opt = 4.2096874633 / 2 * self.sign_vector
        self.x_opt_term = 2 * np.abs(self.true_x_opt)

        self.f_opt = self.raw(self.x_opt)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Schwefel function at a given input vector without any shift.

        The function is calculated as:

            f(X)=-frac{1}{100D}sum_{i=1}^{D}x_i sin(sqrt{| x_i |})

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

        result = -np.sum(x * np.sin(np.sqrt(np.abs(x)))) / \
            (100 * self.dimension)
        return result

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Schwefel function at a given input vector.

        The function is calculated as:

            f(X)=-frac{1}{100D}sum_{i=1}^{D}x_i sin(sqrt{| x_i |}) + 4.189828872724339 + 100f_{pen}(z/100) + f_{opt}

        with the transformations:
            widehat{X} = 2 times 1 pm otimesX
            widehat{z}_i = widehat{x}_i, widehat{z}_{i+1} = widehat{x}_{i+1} + 0.25(widehat{x}_i-[x_i^{opt}longrightarrow 2| x_i^{opt}|])
            z = 100(wedge^{10}(widehat{z}-[x^{opt}longrightarrow 2| x^{opt}|]) + 2| x^{opt}|)


        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Schwefel function.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        x_hat = 2 * self.sign_vector * input_vector

        z_hat = np.zeros(self.dimension, dtype=float)
        z_hat[0] = x_hat[0]

        for i in range(self.dimension - 1):
            z_hat[i+1] = x_hat[i+1] + 0.25 * \
                (x_hat[i] - self.x_opt_term[i])

        diff_vector = z_hat - self.x_opt_term

        lambda_matrix = self.create_diagonal_matrix(10)
        matrix_result = np.matmul(lambda_matrix, diff_vector)

        z = 100 * (matrix_result + self.x_opt_term)

        penalty = 100 * self.f_pen(z / 100)

        raw_value = self.raw(input_vector)

        result = raw_value + 4.189828872724339 + penalty + self.f_opt

        return result
