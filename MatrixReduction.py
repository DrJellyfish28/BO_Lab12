from typing import List, Set, Dict
from enum import Enum, auto
from collections import deque
import numpy as np

# Funkcja redukująca macierz. Zwraca zredukowaną macierz oraz sumę redukcji (LB).

def Matrix_reduction(M : np.ndarray):
    RM = np.zeros(M.shape)
    lb = 0
    for i in range(M.shape[0]):
        minim = np.inf
        for j in range(M.shape[1]):
            if M[i][j] < minim:
                minim = M[i][j]
        for j in range(M.shape[1]):
            RM[i][j] = M[i][j] - minim
        lb += minim

    for i in range(RM.shape[0]):
        minim = np.inf
        for j in range(RM.shape[1]):
            if RM[j][i] < minim:
                minim = RM[j][i]
        for j in range(RM.shape[1]):
            RM[j][i] = RM[j][i] - minim
        lb += minim

    return RM, lb

# Test
MT = np.array([[5,10,15],[5,20,30],[5,50,5]])
print(Matrix_reduction(MT))
MT = np.array([[float('inf'),5,4,6,6],[8,float('inf'),5,3,4],[4,3,float('inf'),3,1],[8,2,5,float('inf'),6],[2,2,7,0,float('inf')]])
print(Matrix_reduction(MT))