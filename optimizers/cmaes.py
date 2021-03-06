import numpy as np
import scipy.linalg as la
import scipy.sparse.linalg as sla

import sys
import os

sys.path.insert(1, os.path.join(os.path.dirname(sys.path[0]), 'environments'))
sys.path.insert(1, os.path.join(os.path.dirname(sys.path[0]), 'optimizers'))
sys.path.insert(1, os.path.dirname(sys.path[0]))

from .optimizer import Optimizer

"""
https://en.wikipedia.org/wiki/CMA-ES
Covariance matrix adaptation evolution strategy for optimization
"""


class CMAES(Optimizer):

    def __init__(self, theta, evaluationFunction):
        self.name = "CMAES"
        self.theta = theta
        self.evaluationFunction = evaluationFunction
        self.N = theta.shape[0]
        self.xmean = np.random.uniform(0, 1, self.N).reshape(-1, 1)
        self.sigma = 0.3
        self.sigma = 0.6
        self.stopfitness = 1e-10
        self.stopfitness = 1e-5
        self.stopeval = 50 * self.N ** 2
        self.stopeval = 50 * self.N
        self.lambd = int(4 + np.floor(3 * np.log(self.N)))
        self.lambd = 50
        self.mu = self.lambd / 2
        self.weights = np.log(self.mu + 1 / 2) - (np.log(range(1, int(self.mu) + 1))).reshape(-1, 1)
        self.mu = int(np.floor(self.mu))
        self.weights = self.weights / np.sum(self.weights)
        self.mueff = (np.sum(self.weights) ** 2) / np.sum(np.power(self.weights, 2))
        self.cc = (4 + self.mueff / self.N) / (self.N + 4 + 2 * self.mueff / self.N)
        self.cs = (self.mueff + 2) / (self.N + self.mueff + 5)
        self.c1 = 2 / ((self.N + 1.3) ** 2 + self.mueff)
        self.cmu = min(1 - self.c1, 2 * (self.mueff - 2 + 1 / self.mueff) / ((self.N + 2) ** 2 + self.mueff))
        self.damps = 1 + 2 * max(0, np.sqrt((self.mueff - 1) / (self.N + 1)) - 1) + self.cs
        self.pc = np.zeros((self.N, 1))
        self.ps = np.zeros((self.N, 1))
        self.B = np.eye(self.N)
        self.D = np.ones((self.N, 1))
        self.C = self.B * np.diag(np.transpose(np.power(self.D, 2))[0]) * np.transpose(self.B)
        self.invsqrtC = self.B * np.diag(np.transpose(np.power(self.D, -1))[0]) * np.transpose(self.B)
        self.eigenval = 0
        self.chiN = self.N ** 0.5 * (1 - 1 / (4 * self.N) + 1 / (21 * self.N ^ 2))
        print(self.name)



    def name(self):
        return self.name

    def run_optimizer(self, verbose=True):
        countEval = 0

        arx = np.zeros((self.N, int(self.lambd)))
        arfitness = np.zeros(int(self.lambd))
        while countEval < self.stopeval:
            for k in range(0, self.lambd):
                arx[:, k] = (self.xmean + self.sigma * np.dot(self.B, (
                        self.D.reshape(-1, 1) * np.random.randn(self.N, 1)))).reshape(self.N, )
                arfitness[k] = self.evaluationFunction(arx[:, k])
                countEval += 1

            arindex = np.argsort(arfitness)
            arfitness = arfitness[arindex]

            xold = self.xmean
            self.xmean = arx[:, arindex[:self.mu]] @ self.weights

            self.ps = (1 - self.cs) * self.ps + np.sqrt(self.cs * (2 - self.cs) * self.mueff) * self.invsqrtC * (
                    self.xmean - xold) / self.sigma
            hsig = np.linalg.norm(self.ps, 2) / np.sqrt(
                1 - (1 - self.cs) ** (2 * countEval / self.lambd)) / self.chiN < 1.4 + 2 / (self.N + 1)
            self.pc = (1 - self.cc) * self.pc + hsig * np.sqrt(self.cc * (2 - self.cc) * self.mueff) * (
                    self.xmean - xold) / self.sigma

            artmp = (1 / self.sigma) * (arx[:, arindex[:self.mu]] - np.tile(xold, (1, self.mu)))

            self.C = (1 - self.c1 - self.cmu) * self.C + self.c1 * (
                    self.pc * np.transpose(self.pc) + (1 - hsig) * self.cc * (
                    2 - self.cc) * self.C) + self.cmu * artmp.dot(np.diag(np.transpose(self.weights)[0])).dot(
                np.transpose(artmp))

            self.sigma = self.sigma * np.exp((self.cs / self.damps) * (np.linalg.norm(self.ps) / self.chiN - 1))

            if countEval - self.eigenval > self.lambd / (self.c1 + self.cmu) / self.N / 10:
                self.eigenval = countEval

                self.C = np.triu(self.C) + np.transpose(np.triu(self.C, 1))
                try:
                    self.D, self.B = np.linalg.eig(self.C)

                except:
                    print("Error", self.C)
                    exit()
                self.D = np.sqrt(self.D).reshape(self.N, 1)
                self.invsqrtC = self.B * np.diag(np.transpose(np.power(self.D, -1))[0]) * np.transpose(self.B)

            if arfitness[0] <= self.stopfitness or (np.max(self.D) > (1e7 * np.min(self.D))):
                print(np.max(self.D) > 1e7 * np.min(self.D))
                print(arfitness[0] <= self.stopfitness)
                break

            if verbose:
                print(f'At iteration count{countEval/self.lambd} best objective is {arfitness[0]}')
                # print(f'Theta value is {arx[:, arindex[0]]}')
                sys.stdout.flush()

        xmin = arx[:, arindex[0]]
        return xmin




def func(x):
    f = 4 + np.dot(x, x)
    return f


def test():
    cem = CMAES(np.array([10,20]), func)
    cem.run_optimizer()


if __name__ == "__main__":
    test()
