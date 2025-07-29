import numpy as np


class Benchmark:
    """
    A base class for benchmark functions used in optimization.

    Attributes:
        dimension (int): The number of dimensions for the input space. Must be a positive integer.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
        shift (np.ndarray): A shift vector for adjusting the input vector.
        f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
    """

    def __init__(self, dimension: int) -> None:
        """
        Initializes the Benchmark class with a rotation matrix and a shift vector.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.

        Raises:
            ValueError: If `dimension` is not a positive integer.
        """
        if not isinstance(dimension, int):
            raise ValueError("dimension must be integer")
        if dimension < 0:
            raise ValueError("dimension must be positive integer")
        if dimension < 1:
            raise ValueError("dimension cannot be zero")
        self.dimension = dimension

    def cec_init(self, rotation: np.ndarray, shift: np.ndarray, f_bias: float = 0) -> None:
        """
        Initializes the cec function class with a rotation matrix and a shift vector.

        Parameters:
            rotation (np.ndarray): The rotation matrix.
            shift (np.ndarray): The shift vector.
            f_bias (float): A bias term added to the benchmark function's output. Defaults to 0.
        """
        if not isinstance(rotation, np.ndarray) or rotation.ndim != 2:
            raise ValueError(
                "Rotation matrix must be a non-empty np.ndarray")
        if rotation.shape[0] != self.dimension and shift.shape[0] != self.dimension:
            raise ValueError(
                "rotation dimension and shift dimension does not match dimension")
        elif rotation.shape[0] != self.dimension:
            raise ValueError(
                "rotation dimension does not match dimension")
        elif shift.shape[0] != self.dimension:
            raise ValueError(
                "shift dimension does not match dimension")
        if rotation.shape[0] != rotation.shape[1]:
            raise ValueError("Rotation matrix must be a square matrix")
        if rotation.shape[0] != shift.shape[0]:
            raise ValueError("rotation and shift has different dimensions")
        self.rotation = rotation
        self.shift = shift
        if not isinstance(f_bias, (float, int)):
            raise ValueError(
                "f_bias must be float or int")
        self.f_bias = float(f_bias)

    def coco_init(self, rotation: np.ndarray) -> None:
        """
        Initializes the coco function class with a rotation matrix.

        Parameters:
            rotation (np.ndarray): The rotation matrix.
        """
        if not isinstance(rotation, np.ndarray) or rotation.ndim != 2:
            raise ValueError(
                "Rotation matrix must be a non-empty np.ndarray")
        elif rotation.shape[0] != self.dimension:
            raise ValueError(
                "rotation dimension does not match dimension")
        if rotation.shape[0] != rotation.shape[1]:
            raise ValueError("Rotation matrix must be a square matrix")
        self.rotation = rotation

    def euclidean_norm(self, input_vector: np.ndarray) -> float:
        """
        Computes the Euclidean norm (L2 norm) of a given input vector.

        Parameters:
            input_vector (np.ndarray): A vector of real numbers.

        Returns:
            float: The Euclidean norm of the input vector.

        Raises:
            ValueError: If the input vector is empty.
        """
        if input_vector.size == 0:
            raise ValueError("Input vector cannot be empty.")
        return np.linalg.norm(input_vector)

    def create_diagonal_matrix(self, alpha: float) -> np.ndarray:
        """
        Creates a diagonal matrix Λ^α, where the diagonal elements are powers of α.

        The diagonal elements are defined as:
            Λ_ii = alpha^(0.5 * (i - 1) / (D - 1)) for i = 1, 2, ..., D,
            where D is the dimension.

        Parameters:
            alpha (float): The base value for the diagonal elements.

        Returns:
            np.ndarray: A diagonal matrix of shape (D, D), where D is the dimension.

        Notes:
            - If the dimension is 1, the matrix is [[1]].
            - If alpha is 0, the matrix is a zero matrix.
        """
        if self.dimension == 1:
            return np.array([[1.0]])

        if alpha == 0:
            return np.zeros((self.dimension, self.dimension))

        exponents = 0.5 * np.arange(self.dimension) / (self.dimension - 1)
        diagonal = alpha ** exponents
        return np.diag(diagonal)

    def generate_random_matrix(self, D: int) -> np.ndarray:
        """
        Generates a random matrix with elements drawn from a standard normal distribution.

        Parameters:
            D (int): The size of the matrix (D x D).

        Returns:
            np.ndarray: A random matrix of shape (D, D).
        """
        return np.random.randn(D, D)

    def matrix_transpose(self, matrix: np.ndarray) -> np.ndarray:
        """
        Computes the transpose of a given matrix.

        Parameters:
            matrix (np.ndarray): A matrix of shape (M, N).

        Returns:
            np.ndarray: The transpose of the matrix, of shape (N, M).
        """
        return matrix.T

    def T_asy_beta(self, beta: float, input_vector: np.ndarray) -> np.ndarray:
        """
        Applies the T_asy^beta transformation to a given input vector.

        The transformation is defined as:
            T_asy^beta(x_i) = x_i^(1 + beta * (i / (D - 1)) * sqrt(x_i)) if x_i > 0,
            T_asy^beta(x_i) = x_i otherwise.

        Parameters:
            beta (float): The beta parameter controlling the transformation.
            input_vector (np.ndarray): A vector of real numbers.

        Returns:
            np.ndarray: The transformed vector.

        Notes:
            - If the dimension is 1, the input vector is returned unchanged.
        """
        if self.dimension == 1:
            return input_vector

        i = np.arange(self.dimension)
        mask = input_vector > 0
        exponent = 1 + beta * (i / (self.dimension - 1)
                               ) * np.sqrt(input_vector)
        result = np.where(mask, input_vector ** exponent, input_vector)
        return result

    def T_osz(self, input_vector: np.ndarray) -> np.ndarray:
        """
        Applies the T_osz transformation to a given input vector.

        The transformation is defined as:
            T_osz(x_i) = sign(x_i) * exp(x_hat + 0.049 * (sin(c1 * x_hat) + sin(c2 * x_hat))),
            where x_hat = log(|x_i|) if x_i ≠ 0, and 0 otherwise.

        Parameters:
            input_vector (np.ndarray): A vector of real numbers.

        Returns:
            np.ndarray: The transformed vector.

        Notes:
            - The transformation is applied element-wise.
            - If x_i is 0, the result is 0.
        """
        x_hat = np.where(input_vector == 0, 0, np.log(np.abs(input_vector)))
        sign = np.sign(input_vector)
        c1 = np.where(input_vector > 0, 10, 5.5)
        c2 = np.where(input_vector > 0, 7.9, 3.1)
        transformed = np.exp(
            x_hat + 0.049 * (np.sin(c1 * x_hat) + np.sin(c2 * x_hat)))
        return np.where(input_vector == 0, 0, sign * transformed)

    def elementwise_multiply(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Performs element-wise multiplication of two vectors or matrices.

        Parameters:
            x (np.ndarray): The first input array.
            y (np.ndarray): The second input array.

        Returns:
            np.ndarray: The element-wise product of x and y.

        Raises:
            ValueError: If the shapes of x and y do not match.
        """
        if x.shape != y.shape:
            raise ValueError("Vectors must have the same length.")
        return x * y

    def f_pen(self, x: np.ndarray) -> float:
        """
        Computes the penalty function for a given input vector.

        The penalty function is defined as:
            f_pen(x) = sum(max(0, |x_i| - 5)^2).

        Parameters:
            x (np.ndarray): A vector of real numbers.

        Returns:
            float: The penalty value.
        """
        return np.sum(np.maximum(0, np.abs(x) - 5) ** 2)

    def gram_schmidt(self, matrix: np.ndarray) -> np.ndarray:
        """
        Applies the Gram-Schmidt process to a set of vectors.

        This method orthogonalizes the input vectors (columns of the matrix) and normalizes them to unit length.

        Parameters:
            matrix (np.ndarray): A 2D array where each column is a vector.

        Returns:
            np.ndarray: A 2D array with orthogonal and normalized vectors as columns.

        Notes:
            - If the input vectors are linearly dependent, the output will contain zero vectors for dependent columns.
            - Uses floating-point arithmetic, so results may have small numerical errors.
        """
        matrix = np.array(matrix, dtype=np.float64)
        Q = np.zeros_like(matrix)

        for j in range(matrix.shape[1]):
            v = matrix[:, j]
            for i in range(j):
                v -= np.dot(Q[:, i], v) * Q[:, i]
            norm = np.linalg.norm(v)
            Q[:, j] = v / norm if norm > 1e-14 else 0

        return Q
