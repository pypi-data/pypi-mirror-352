import numpy as np


class IntervalMatrix3DSolver:
    @staticmethod
    def interval_determinant_bounds_3d(lower_matrices, upper_matrices):
        """
        Приближённая оценка интервала возможных значений определителя для набора интервальных матриц 3D.

        lower_matrices, upper_matrices — numpy массивы размерности (N, n, n),
        где N — количество матриц, n x n — размер каждой матрицы.

        Возвращает список кортежей (min_det, max_det) для каждой матрицы.
        """
        results = []
        for i in range(lower_matrices.shape[0]):
            lower = lower_matrices[i]
            upper = upper_matrices[i]
            mid = (lower + upper) * 0.5
            rad = (upper - lower) * 0.5
            center_det = np.linalg.det(mid)
            delta = np.sum(np.abs(rad))
            results.append((center_det - delta, center_det + delta))
        return results

    @staticmethod
    def interval_solve_bounds_3d(A_lower_3d, A_upper_3d, b_lower_2d, b_upper_2d):
        """
        Приближенное интервальное решение набора систем СЛАУ.

        A_lower_3d, A_upper_3d — numpy массивы (N, n, n), интервалы для матриц коэффициентов,
        b_lower_2d, b_upper_2d — numpy массивы (N, n), интервалы для векторов свободных членов.

        Возвращает список списков кортежей (min_x_i, max_x_i) по каждому решению.
        """
        results = []
        N = A_lower_3d.shape[0]
        for i in range(N):
            A_lower = A_lower_3d[i]
            A_upper = A_upper_3d[i]
            b_lower = b_lower_2d[i]
            b_upper = b_upper_2d[i]

            A_mid = (A_lower + A_upper) * 0.5
            b_mid = (b_lower + b_upper) * 0.5
            try:
                x_mid = np.linalg.solve(A_mid, b_mid)
            except np.linalg.LinAlgError:
                results.append("Матрица вырождена, решение невозможно")
                continue

            A_rad = (A_upper - A_lower) * 0.5
            b_rad = (b_upper - b_lower) * 0.5
            delta_x = np.full_like(x_mid, 0.0)

            for j in range(len(x_mid)):
                delta_x[j] = np.sum(np.abs(A_rad)) + np.sum(np.abs(b_rad))

            x_lower = x_mid - delta_x
            x_upper = x_mid + delta_x
            results.append(list(zip(x_lower, x_upper)))
        return results
