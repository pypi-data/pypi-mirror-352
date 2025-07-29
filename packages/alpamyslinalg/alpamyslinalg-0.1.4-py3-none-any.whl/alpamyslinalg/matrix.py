import numpy as np

class Matrix:
    def __init__(self, data):
        # data — это список списков, например [[1,2],[3,4]]
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

    def __str__(self):
        return '\n'.join(['\t'.join(map(str, row)) for row in self.data])

    def __add__(self, other):
        # Сложение матриц
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Матрицы должны быть одного размера")
        result = [
            [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ]
        return Matrix(result)

    def __sub__(self, other):
        # Вычитание матриц
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Матрицы должны быть одного размера")
        result = [
            [self.data[i][j] - other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ]
        return Matrix(result)

    def __mul__(self, other):
        # Умножение матриц
        if self.cols != other.rows:
            raise ValueError("Число столбцов первой матрицы должно быть равно числу строк второй")
        result = []
        for i in range(self.rows):
            row = []
            for j in range(other.cols):
                s = 0
                for k in range(self.cols):
                    s += self.data[i][k] * other.data[k][j]
                row.append(s)
            result.append(row)
        return Matrix(result)

    def determinant(self):
        # Для простоты только 2x2
        if self.rows != 2 or self.cols != 2:
            raise NotImplementedError("Определитель реализован только для 2x2")
        return self.data[0][0]*self.data[1][1] - self.data[0][1]*self.data[1][0]

    def inverse(self):
        # Только для 2x2
        det = self.determinant()
        if det == 0:
            raise ValueError("Обратной матрицы не существует")
        result = [
            [ self.data[1][1]/det, -self.data[0][1]/det],
            [-self.data[1][0]/det,  self.data[0][0]/det]
        ]
        return Matrix(result)

    def solve(self, b):
        # Решение системы Ax = b, где A — self, b — вектор (список)
        if self.rows != 2 or self.cols != 2:
            raise NotImplementedError("Решение реализовано только для 2x2 систем")
        inv = self.inverse()
        # Умножаем матрицу inverse на вектор b
        result = []
        for i in range(inv.rows):
            s = 0
            for j in range(inv.cols):
                s += inv.data[i][j] * b[j]
            result.append(s)
        return result

    def cramer_method(A, B):
        """
        Решение системы линейных уравнений методом Крамера.

        A - квадратная матрица коэффициентов
        B - столбец свободных членов
        """
        det_A = np.linalg.det(A)  # Определитель матрицы A
        if det_A == 0:
            return "Решение невозможно: определитель матрицы равен нулю"

        n = len(B)
        solutions = []

        for i in range(n):
            Ai = A.copy()
            Ai[:, i] = B  # Заменяем i-й столбец матрицы A на столбец B
            det_Ai = np.linalg.det(Ai)  # Вычисляем определитель новой матрицы
            solutions.append(det_Ai / det_A)  # Вычисляем значение переменной

        return solutions


    def gauss_elimination(A, B):
        """
        Численный метод Гаусса для решения системы линейных уравнений.

        A - матрица коэффициентов
        B - столбец свободных членов
        """
        n = len(B)
        A = A.astype(float)  # Преобразуем в тип float для точности
        B = B.astype(float)

        # Прямой ход (приведение к верхнетреугольному виду)
        for i in range(n):
            # Нормализация ведущего элемента
            pivot = A[i, i]
            for j in range(i, n):
                A[i, j] /= pivot
            B[i] /= pivot

            # Обнуление элементов ниже ведущего
            for k in range(i + 1, n):
                factor = A[k, i]
                for j in range(i, n):
                    A[k, j] -= factor * A[i, j]
                B[k] -= factor * B[i]

        # Обратный ход (нахождение решений)
        X = np.zeros(n)
        for i in range(n - 1, -1, -1):
            X[i] = B[i] - sum(A[i, j] * X[j] for j in range(i + 1, n))

        return X

  
  
  
  
  
  
  
  
  
  
  
  

  
  
  
  
  
  
  
  
  
  
  
  

  
  
  
  

  
  

  
  
  

