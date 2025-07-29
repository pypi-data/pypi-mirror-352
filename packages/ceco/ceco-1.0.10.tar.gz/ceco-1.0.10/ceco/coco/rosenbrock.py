import numpy as np
from ceco.benchmark import Benchmark


class Rosenbrock(Benchmark):
    """
    A class representing the Rosenbrock function, which is a benchmark function
    for optimization.

    The Rosenbrock function is defined as:

        f(X)=sum_{i=1}^{D-1}( 100( z_i^2-z_{i+1} )^2+( z_i-1 )^2 )+f_opt

    where x is an input vector of dimension D.

    This class inherits from `Benchmark` and applies a shift transformation to the input vector. The optimal solution (x_opt) is randomly generated within the range [-5, 5], and the function value at x_opt (f_opt) computed as f(x_opt).

    Attributes:
        x_opt (np.ndarray): The optimal shift vector, randomly generated within [-5, 5].
        f_opt (float): The function value at x_opt.
        rotation (np.ndarray): A rotation matrix for transforming the input vector.
    """

    def __init__(self, dimension: int, rotation: np.ndarray = None) -> None:
        """
        Initializes the Rosenbrock function with a given dimension.

        Parameters:
            dimension (int): The number of dimensions for the input space. Must be a positive integer.
            rotation (np.ndarray): A rotation matrix for transforming the input vector. Defaults to None (no rotation).

        Raises:
            ValueError: If dimension is not a positive integer.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("Dimension must be a positive integer")
        super().__init__(dimension)
        # Generate a random optimal solution vector x_opt within the range [-5, 5]
        self.x_opt = np.random.uniform(-5, 5, dimension)

        self.f_opt = self.raw(self.x_opt)

        self.identity_matrix = np.eye(dimension)
        self.scaling_factor = max(1, dimension / 8)

        if rotation is not None:
            self.rotation = self.gram_schmidt(rotation)
        else:
            self.rotation = self.identity_matrix

        self.coco_init(rotation)

    def raw(self, x: np.ndarray) -> float:
        """
        Evaluates the Rosenbrock function at a given input vector without any shift.

        The function is calculated as:

        f(X)=sum_{i=1}^{D-1}( 100( x_i^2-x_i+1 )^2+( x_i-1 )^2 )

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

        xi = x[:-1]
        xi1 = x[1:]
        return np.sum(100.0 * (xi**2 - xi1)**2 + (xi - 1)**2)

    def evaluate(self, input_vector: np.ndarray) -> float:
        """
        Evaluates the Rosenbrock function at a given input vector.

        The function is calculated as:

        f(X)=sum_{i=1}^{D-1}( 100( z_i^2-z_{i+1} )^2+( z_i-1 )^2 )+f_opt

        Parameters:
            input_vector (np.ndarray): A vector of real numbers representing a candidate solution. Must have the same length as the dimension of the Rosenbrock function.
            rotation_matrix (np.ndarray, optional): A rotation matrix to apply to the input vector. Required if `rotation` is True.

        Returns:
            float: The function value at the given input vector.

        Raises:
            ValueError: If the input vector does not match the expected dimension.
        """
        if input_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Input vector must have {self.dimension} elements")

        if np.allclose(self.rotation, np.eye(self.dimension)):
            z = self.scaling_factor * (input_vector - self.x_opt) + 1
        else:
            z = self.scaling_factor * \
                self.gram_schmidt(self.rotation.T) @ input_vector + (1 / 2)
        result = self.raw(z) + self.f_opt

        return result
