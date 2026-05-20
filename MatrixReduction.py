from typing import List, Set, Dict
from enum import Enum, auto
from collections import deque
import numpy as np

# Funkcja redukująca macierz. Zwraca zredukowaną macierz (sumę redukcji należy odkomentować).

def Matrix_reduction(M : np.ndarray):
    RM = np.zeros(M.shape)
    #sr = 0
    for i in range(M.shape[0]):
        minim = np.inf
        for j in range(M.shape[1]):
            if M[i][j] < minim:
                minim = M[i][j]
        for j in range(M.shape[1]):
            RM[i][j] = M[i][j] - minim
        #sr += minim

    for i in range(RM.shape[0]):
        minim = np.inf
        for j in range(RM.shape[1]):
            if RM[j][i] < minim:
                minim = RM[j][i]
        for j in range(RM.shape[1]):
            RM[j][i] = RM[j][i] - minim
        #sr += minim

    return RM #, sr

# Test
MT = np.array([[5,10,15],[5,20,30],[5,50,5]])
print(Matrix_reduction(MT))