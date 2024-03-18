#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 12

void generate_random_matrix(double matrix[SIZE][SIZE]) {
    srand(time(0));
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            matrix[i][j] = (double)rand() / RAND_MAX;
        }
    }
}

void multiply(double a[SIZE][SIZE], double b[SIZE][SIZE], double result[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            result[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }
}

int main() {
    double a[SIZE][SIZE], b[SIZE][SIZE], result[SIZE][SIZE];
    generate_random_matrix(a);
    generate_random_matrix(b);
    multiply(a, b, result);
    return 0;
}
