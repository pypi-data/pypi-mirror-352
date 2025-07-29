import unittest
import numpy as np
from ceco.benchmark import Benchmark


class Test_benchmark(unittest.TestCase):
    def setUp(self):
        # Example rotation matrix and shift vector for testing
        # Identity matrix (no rotation)
        self.input_2d = np.array([3, 2])
        self.input_3d = np.array([3, 2, 1])
        self.no_rotation_2d = np.array([[1, 0], [0, 1]])
        self.no_rotation_3d = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.rotation_2d = np.array([[0, -1], [1, 0]])  # 90-degree rotation
        self.rotation_3d = np.array(
            [[0, -1, 0], [1, 0, 0], [0, 0, 1]])  # 90-degree rotation
        self.shift_2d = np.array([1, 1])  # Shift vector
        self.no_shift_2d = np.array([0, 0])  # No shift vector
        self.shift_3d = np.array([1, 1, 1])  # Shift vector
        self.no_shift_3d = np.array([0, 0, 0])  # No shift vector
        self.f_bias = 100

    def test_initialization_2d_no_rotation_no_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.no_rotation_2d, self.no_shift_2d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.no_rotation_2d, benchmark.rotation)
        np.testing.assert_array_equal(self.no_shift_2d, benchmark.shift)

    def test_initialization_3d_no_rotation_no_shift(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.no_rotation_3d, self.no_shift_3d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.no_rotation_3d, benchmark.rotation)
        np.testing.assert_array_equal(self.no_shift_3d, benchmark.shift)

    def test_initialization_2d_rotation_no_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.rotation_2d, self.no_shift_2d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.rotation_2d, benchmark.rotation)
        np.testing.assert_array_equal(self.no_shift_2d, benchmark.shift)

    def test_initialization_3d_rotation_no_shift(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.rotation_3d, self.no_shift_3d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.rotation_3d, benchmark.rotation)
        np.testing.assert_array_equal(self.no_shift_3d, benchmark.shift)

    def test_initialization_2d_rotation_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.rotation_2d, self.shift_2d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.rotation_2d, benchmark.rotation)
        np.testing.assert_array_equal(self.shift_2d, benchmark.shift)

    def test_initialization_3d_rotation_shift(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.rotation_3d, self.shift_3d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.rotation_3d, benchmark.rotation)
        np.testing.assert_array_equal(self.shift_3d, benchmark.shift)

    def test_initialization_2d_no_rotation_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.no_rotation_2d, self.shift_2d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.no_rotation_2d, benchmark.rotation)
        np.testing.assert_array_equal(self.shift_2d, benchmark.shift)

    def test_initialization_3d_no_rotation_shift(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.no_rotation_3d, self.shift_3d)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.no_rotation_3d, benchmark.rotation)
        np.testing.assert_array_equal(self.shift_3d, benchmark.shift)

    def test_mismatch_dimension_rotation_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        with self.assertRaises(ValueError) as context:
            benchmark.cec_init(self.no_rotation_3d, self.no_shift_3d)
        self.assertEqual(str(context.exception),
                         "rotation dimension and shift dimension does not match dimension")

    def test_mismatch_dimension_rotation(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        with self.assertRaises(ValueError) as context:
            benchmark.cec_init(self.no_rotation_3d, self.no_shift_2d)
        self.assertEqual(str(context.exception),
                         "rotation dimension does not match dimension")

    def test_mismatch_dimension_shift(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        with self.assertRaises(ValueError) as context:
            benchmark.cec_init(self.no_rotation_2d, self.no_shift_3d)
        self.assertEqual(str(context.exception),
                         "shift dimension does not match dimension")

    def test_negative_dimension(self):
        dimension = -1
        with self.assertRaises(ValueError) as context:
            benchmark = Benchmark(dimension)
        self.assertEqual(str(context.exception),
                         "dimension must be positive integer")

    def test_zero_dimension(self):
        dimension = 0
        with self.assertRaises(ValueError) as context:
            benchmark = Benchmark(dimension)
        self.assertEqual(str(context.exception),
                         "dimension cannot be zero")

    def test_non_int_dimension(self):
        float = 1.0
        string = "abc"
        li = [1, 2, 3]
        with self.assertRaises(ValueError) as context:
            benchmark = Benchmark(float)
            self.assertEqual(str(context.exception),
                             "dimension must be integer")
            benchmark = Benchmark(string)
            self.assertEqual(str(context.exception),
                             "dimension must be integer")
            benchmark = Benchmark(li)
            self.assertEqual(str(context.exception),
                             "dimension must be integer")

    def test_initialization_f_bias(self):
        dimension = 2
        benchmark = Benchmark(dimension)
        benchmark.cec_init(self.rotation_2d, self.shift_2d, self.f_bias)
        self.assertEqual(dimension, benchmark.dimension)
        np.testing.assert_array_equal(self.rotation_2d, benchmark.rotation)
        np.testing.assert_array_equal(self.shift_2d, benchmark.shift)
        self.assertEqual(self.f_bias, benchmark.f_bias)

    def test_not_int_not_float_f_bias(self):
        dimension = 2
        string = "abc"
        li = [1, 2, 3]
        benchmark = Benchmark(dimension)
        with self.assertRaises(ValueError) as context:
            benchmark.cec_init(self.no_rotation_2d, self.no_shift_2d, string)
            self.assertEqual(str(context.exception),
                             "f_bias must be float or int")
        with self.assertRaises(ValueError) as context:
            benchmark.cec_init(self.no_rotation_2d, self.no_shift_2d, li)
            self.assertEqual(str(context.exception),
                             "f_bias must be float or int")

    # Test Euclidean Norm
    def test_euclidean_norm(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        input_vector = np.array([3, 4, 0])
        expected = 5.0  # sqrt(3^2 + 4^2)
        result = benchmark.euclidean_norm(input_vector)
        self.assertAlmostEqual(result, expected)

    def test_euclidean_norm_empty_vector(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        input_vector = np.array([])
        with self.assertRaises(ValueError):
            benchmark.euclidean_norm(input_vector)

    def test_euclidean_norm_single_element(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        input_vector = np.array([5])
        expected = 5.0
        result = benchmark.euclidean_norm(input_vector)
        self.assertAlmostEqual(result, expected)

    # Test Diagonal Matrix
    def test_create_diagonal_matrix(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        alpha = 2
        expected = np.diag([2**0, 2**(0.5 * 1 / 2), 2**(0.5 * 2 / 2)])
        result = benchmark.create_diagonal_matrix(alpha)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_create_diagonal_matrix_dimension_one(self):
        dimension = 1
        benchmark = Benchmark(dimension)
        alpha = 2
        expected = np.array([[1.0]])
        result = benchmark.create_diagonal_matrix(alpha)
        np.testing.assert_array_almost_equal(result, expected)

    def test_create_diagonal_matrix_zero_alpha(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        alpha = 0
        expected = np.zeros((dimension, dimension))
        result = benchmark.create_diagonal_matrix(alpha)
        np.testing.assert_array_almost_equal(result, expected)

    # Test Random Matrix
    def test_generate_random_matrix(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        matrix = benchmark.generate_random_matrix(dimension)
        self.assertEqual(matrix.shape, (dimension, dimension))

    # Test T_asy_beta
    def test_T_asy_beta(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        beta = 1.0
        input_vector = np.array([1, 2, 3])
        expected = np.array([
            1 ** (1 + beta * 0 / 2 * np.sqrt(1)),
            2 ** (1 + beta * 1 / 2 * np.sqrt(2)),
            3 ** (1 + beta * 2 / 2 * np.sqrt(3))
        ])
        result = benchmark.T_asy_beta(beta, input_vector)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_T_asy_beta_negative(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        beta = 1.0
        input_vector = np.array([-1, -2, -3])
        expected = input_vector
        result = benchmark.T_asy_beta(beta, input_vector)
        np.testing.assert_array_equal(result, expected)

    # Test T_osz
    def test_T_osz(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        input_vector = np.array([1, -1, 0])
        result = benchmark.T_osz(input_vector)

        expected = np.array([
            np.exp(np.log(1) + 0.049 *
                   (np.sin(10 * np.log(1)) + np.sin(7.9 * np.log(1)))),
            -np.exp(np.log(1) + 0.049 *
                    (np.sin(5.5 * np.log(1)) + np.sin(3.1 * np.log(1)))),
            0
        ])
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_T_osz_zero_vector(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        input_vector = np.array([0, 0, 0])
        expected = np.array([0, 0, 0])
        result = benchmark.T_osz(input_vector)
        np.testing.assert_array_equal(result, expected)

    # Test Element-wise Multiplication
    def test_elementwise_multiply(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        expected = np.array([4, 10, 18])
        result = benchmark.elementwise_multiply(x, y)
        np.testing.assert_array_equal(result, expected)

    def test_elementwise_multiply_invalid(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        x = np.array([1, 2, 3])
        y = np.array([4, 5])
        with self.assertRaises(ValueError):
            benchmark.elementwise_multiply(x, y)

    # Test f_pen
    def test_f_pen_no_penalty(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        x = np.array([1, 2, 3])
        result = benchmark.f_pen(x)
        self.assertAlmostEqual(result, 0.0)

    def test_f_pen_partial_penalty(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        x = np.array([1, 6, 3])
        result = benchmark.f_pen(x)
        self.assertAlmostEqual(result, 1.0)

    def test_f_pen_all_penalty(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        x = np.array([6, 7, 8])
        result = benchmark.f_pen(x)
        self.assertAlmostEqual(result, 14.0)

    # Test gram schmidt
    def test_gram_schmidt_orthogonalization(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 1, 1],
                      [0, 1, 1],
                      [0, 0, 1]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that all pairs of columns are orthogonal
        for i in range(Q.shape[1]):
            for j in range(i + 1, Q.shape[1]):
                dot_product = np.dot(Q[:, i], Q[:, j])
                self.assertTrue(np.isclose(dot_product, 0, atol=1e-10),
                                f"Vectors {i} and {j} are not orthogonal.")

    def test_gram_schmidt_normalization(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 2, 3],
                      [0, 1, 2],
                      [0, 0, 1]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that each column vector has unit length
        for i in range(Q.shape[1]):
            norm = np.linalg.norm(Q[:, i])
            self.assertTrue(np.isclose(norm, 1, atol=1e-10),
                            f"Vector {i} is not normalized.")

    def test_gram_schmidt_linearly_dependent_vectors(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 2, 3],
                      [2, 4, 6],
                      [3, 6, 9]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the last vector is zero (due to linear dependence)
        self.assertTrue(np.allclose(Q[:, 2], np.zeros(Q.shape[0])),
                        "Linearly dependent vectors were not handled correctly.")

    def test_gram_schmidt_identity_matrix(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.eye(3)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the output is the same as the input
        self.assertTrue(np.allclose(Q, A),
                        "Identity matrix was not preserved.")

    def test_gram_schmidt_zero_matrix(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.zeros((3, 3))

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the output is also a zero matrix
        self.assertTrue(np.allclose(Q, A),
                        "Zero matrix was not preserved.")

    def test_gram_schmidt_non_square_matrix(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 2, 3],
                      [0, 1, 2]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the output vectors are orthogonal and normalized
        for i in range(Q.shape[1]):
            for j in range(i + 1, Q.shape[1]):
                dot_product = np.dot(Q[:, i], Q[:, j])
                self.assertTrue(np.isclose(dot_product, 0, atol=1e-10),
                                f"Vectors {i} and {j} are not orthogonal.")

            # Check if the vector is effectively zero (due to linear dependence)
            norm = np.linalg.norm(Q[:, i])
            if np.isclose(norm, 0, atol=1e-10):
                # If the vector is zero, skip normalization check
                self.assertTrue(np.allclose(Q[:, i], np.zeros(Q.shape[0])),
                                f"Vector {i} is not zero.")
            else:
                # Otherwise, check that the vector is normalized
                self.assertTrue(np.isclose(norm, 1, atol=1e-10),
                                f"Vector {i} is not normalized.")

    def test_gram_schmidt_matrix_values_non_orthogonal(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 1, 1],
                      [1, 0, 1],
                      [0, 1, 1]], dtype=float)

        # Expected orthogonalized matrix (precomputed using a trusted implementation)
        expected_Q = np.array([[0.70710678, 0.40824829, -0.57735027],
                               [0.70710678, -0.40824829, 0.57735027],
                               [0.0, 0.81649658, 0.57735027]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the output matches the expected result
        self.assertTrue(np.allclose(Q, expected_Q, atol=1e-8),
                        "Output matrix does not match the expected result.")

    def test_gram_schmidt_bigger_dimension(self):
        dimension = 3
        benchmark = Benchmark(dimension)
        A = np.array([[1, 1, 1, 0, 0],
                      [1, 0, 1, 0, 0],
                      [0, 1, 1, 0, 0],
                      [0, 0, 0, 1, 0],
                      [0, 0, 0, 0, 1]], dtype=float).T

        expected_Q = np.array([[0.57735027, 0.40824829, -0.70710678, 0, 0],
                               [0.57735027, -0.81649658, 0.0, 0, 0],
                               [0.57735027, 0.40824829, 0.70710678, 0, 0],
                               [0, 0, 0, 1, 0],
                               [0, 0, 0, 0, 1]], dtype=float)

        # Apply Gram-Schmidt
        Q = benchmark.gram_schmidt(A)

        # Verify that the output matches the expected result
        self.assertTrue(np.allclose(Q, expected_Q, atol=1e-8),
                        "Output matrix does not match the expected result.")


if __name__ == '__main__':
    unittest.main()
