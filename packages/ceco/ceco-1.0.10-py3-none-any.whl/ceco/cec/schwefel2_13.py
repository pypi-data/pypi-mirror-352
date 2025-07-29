from ceco.benchmark import Benchmark
import numpy as np


class Schwefel2_13(Benchmark):
    """
    A class representing the Schwefel 2.13 function, which is a benchmark function
    for optimization.

    This function is commonly used to test optimization algorithms due to its complex
    and multi-modal nature. The class inherits from the `Benchmark` class and applies
    rotation and shift transformations to the input vector before evaluating the function.

    The Schwefel 2.13 function is defined as:
    F(X) = sum_{i=1 to D} (A_i - B_i(X))^2,
    where:
    - A_i = sum_{j=1 to D} (a_{ij} * sin(alpha_j) + b_{ij} * cos(alpha_j)),
    - B_i(X) = sum_{j=1 to D} (a_{ij} * sin(x_j) + b_{ij} * cos(x_j)).

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        a (list of list of int): A D x D matrix of random integers in the range [-100, 100].
        b (list of list of int): A D x D matrix of random integers in the range [-100, 100].
        alpha (list of float): A vector of D random numbers in the range [-π, π].
    """

    def __init__(self, dimension: int, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the Schwefel2_13 class with a rotation matrix, shift vector, and dimension.

        During initialization, random matrices `a` and `b` and a random vector `alpha` are
        generated. These are used to define the Schwefel 2.13 function.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): The rotation matrix for transforming the input vector.
            shift (np.ndarray): The shift vector for adjusting the input vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        super().__init__(dimension)
        self.cec_init(rotation, shift, f_bias)

        # Generate random matrices a and b
        self.a = self.generate_random_matrix(self.dimension, -100, 100)
        self.b = self.generate_random_matrix(self.dimension, -100, 100)

        # Generate random alpha vector
        self.alpha = self.generate_random_alpha(self.dimension)

    def generate_random_matrix(self, D: int, min_val: int, max_val: int) -> np.ndarray:
        """
        Generates a D x D matrix with random integers in the range [min_val, max_val].

        Parameters:
            D (int): The dimension of the matrix.
            min_val (int): The minimum value for random integers.
            max_val (int): The maximum value for random integers.

        Returns:
            list of list of int: A D x D matrix of random integers.
        """
        return np.random.randint(min_val, max_val + 1, size=(D, D))

    def generate_random_alpha(self, D: int) -> np.ndarray:
        """
        Generates a list of D random numbers in the range [-π, π].

        Parameters:
            D (int): The number of random numbers to generate.

        Returns:
            np.ndarray: A list of D random numbers in the range [-π, π].
        """
        return np.random.uniform(-np.pi, np.pi, size=D)

    def compute_A(self, a: np.ndarray, b: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        """
        Computes the A vector using the formula:
        A_i = sum_{j=1 to D} (a_{ij} * sin(alpha_j) + b_{ij} * cos(alpha_j)).

        Parameters:
            D (int): The dimension of the problem.
            a (np.ndarray): The a matrix.
            b (np.ndarray): The b matrix.
            alpha (np.ndarray): The alpha vector.

        Returns:
            np.ndarray: The computed A vector.
        """
        return np.sum(a * np.sin(alpha) + b * np.cos(alpha), axis=1)

    def compute_B(self, a: np.ndarray, b: np.ndarray, X: np.ndarray) -> np.ndarray:
        """
        Computes the B vector using the formula:
        B_i(X) = sum_{j=1 to D} (a_{ij} * sin(x_j) + b_{ij} * cos(x_j)).

        Parameters:
            D (int): The dimension of the problem.
            a (np.ndarray): The a matrix.
            b (np.ndarray): The b matrix.
            X (np.ndarray): The input vector.

        Returns:
            np.ndarray: The computed B vector.
        """
        return np.sum(a * np.sin(X) + b * np.cos(X), axis=1)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Schwefel 2.13 function at a given input vector after applying
        rotation and shift transformations.

        The function first applies the rotation matrix and shift vector to the input vector.
        Then, it computes the A and B vectors and evaluates the Schwefel 2.13 function:
        F(X) = sum_{i=1 to D} (A_i - B_i(X))^2.

        Parameters:
            input_vector (np.ndarray): The input vector [x1, x2, ..., xD].

        Returns:
            float: The result of the Schwefel 2.13 function after applying rotation and shift.
        """
        # Apply shift and rotation
        shifted_rotated_vector = np.matmul(
            self.rotation, input_vector - self.shift)

        # Compute A and B
        A = self.compute_A(self.a, self.b, self.alpha)
        B = self.compute_B(self.a, self.b, shifted_rotated_vector)

        # Compute the Schwefel 2.13 function
        total_sum = np.sum((A - B) ** 2)

        return total_sum + self.f_bias
