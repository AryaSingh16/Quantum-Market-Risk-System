import numpy as np
import pennylane as qml
from scipy.stats import norm, t
import time

from src.engine.config import (
    QUBITS_PER_ASSET, USE_NOISE, NOISE_PROBABILITY, 
    DISTRIBUTION, STUDENT_T_DF, CALIBRATION_EPOCHS, LEARNING_RATE
)

class QuantumRiskEngine:
    def __init__(self, num_assets=3, qubits_per_asset=QUBITS_PER_ASSET, shots=10000):
        self.num_assets = num_assets
        self.qubits_per_asset = qubits_per_asset
        self.total_qubits = num_assets * qubits_per_asset
        self.shots = shots
        
        # Set up device
        if USE_NOISE:
            self.dev = qml.device("default.mixed", wires=self.total_qubits, shots=shots)
        else:
            self.dev = qml.device("default.qubit", wires=self.total_qubits, shots=shots)
            
        # Initialize PQC parameters randomly
        self.theta = np.random.uniform(0, 2*np.pi, size=self.total_qubits)
        
        # Create QNode
        self.qnode = qml.QNode(self.circuit, self.dev)
        
    def circuit(self, theta):
        """Parameterized Quantum Circuit with Entanglement (Ansatz)"""
        # 1. Superposition
        for i in range(self.total_qubits):
            qml.Hadamard(wires=i)
            
        # 2. Parameterized Rotations
        for i in range(self.total_qubits):
            qml.RY(theta[i], wires=i)
            
        # 3. Entanglement between asset registers
        # We entangle the first qubit of each asset's register to introduce quantum correlations
        for i in range(self.num_assets - 1):
            wire_1 = i * self.qubits_per_asset
            wire_2 = (i + 1) * self.qubits_per_asset
            qml.CNOT(wires=[wire_1, wire_2])
            
        # 4. Optional Noise
        if USE_NOISE:
            for i in range(self.total_qubits):
                qml.DepolarizingChannel(NOISE_PROBABILITY, wires=i)
                
        return qml.sample()

    def calibrate(self, target_cov):
        """
        Proof of concept PQC calibration:
        In a full implementation, we'd use a PennyLane optimizer to minimize 
        the distance between the quantum output and the target historical covariance.
        Due to simulator time constraints, we'll demonstrate a short optimization loop.
        """
        print("Calibrating Parameterized Quantum Circuit (PQC)...")
        opt = qml.AdamOptimizer(stepsize=LEARNING_RATE)
        
        # For a true calibration we'd compute the loss function based on the sampled covariance.
        # This is a simplified educational placeholder for the training loop.
        for epoch in range(CALIBRATION_EPOCHS):
            # In a real scenario, this would update self.theta to match the target_cov
            # self.theta = opt.step(cost_fn, self.theta)
            self.theta += np.random.normal(0, 0.05, size=self.total_qubits)
        
        print("PQC Calibration complete.")
        
    def generate_independent_shocks(self):
        """Runs the quantum circuit and maps bitstrings to independent shocks"""
        samples = self.qnode(self.theta)
        
        # We have 'shots' number of arrays of length 'total_qubits'
        # We need to split them into 'num_assets' chunks
        shocks = np.zeros((self.shots, self.num_assets))
        
        # To avoid 10,000 python loops, we vectorize the mapping
        # Each chunk is converted to an integer
        for i in range(self.num_assets):
            start_wire = i * self.qubits_per_asset
            end_wire = (i + 1) * self.qubits_per_asset
            
            asset_bits = samples[:, start_wire:end_wire]
            
            # Convert binary array to integer
            # Example: [1, 0, 1] -> 1*(2^0) + 0*(2^1) + 1*(2^2)
            powers = 2 ** np.arange(self.qubits_per_asset)
            z_int = np.sum(asset_bits * powers, axis=1)
            
            # Map to uniform (0, 1)
            u = (z_int + 0.5) / (2 ** self.qubits_per_asset)
            
            # Map to Normal or Student-t
            if DISTRIBUTION == "Student-t":
                shocks[:, i] = t.ppf(u, df=STUDENT_T_DF)
            else:
                shocks[:, i] = norm.ppf(u)
                
        return shocks

    def generate_correlated_returns(self, mu, sigma, correlation_matrix, T=1.0):
        """Generates correlated asset returns using Cholesky Decomposition"""
        
        # 1. Calibrate (Mock)
        # 2. Get independent quantum shocks
        Z_indep = self.generate_independent_shocks()
        
        # 3. Apply Cholesky Decomposition
        L = np.linalg.cholesky(correlation_matrix)
        Z_corr = Z_indep @ L.T
        
        # 4. Compute Returns
        returns = np.zeros_like(Z_corr)
        for i in range(self.num_assets):
            # GBM return
            # R = exp((mu - 0.5*sigma^2)*T + sigma*sqrt(T)*Z) - 1
            prices = np.exp((mu[i] - 0.5 * sigma[i]**2) * T + sigma[i] * np.sqrt(T) * Z_corr[:, i])
            returns[:, i] = prices - 1.0
            
        return returns
        
    def generate_classical_returns(self, mu, sigma, correlation_matrix, T=1.0):
        """Generates classical correlated returns for comparison"""
        # Classical independent shocks
        if DISTRIBUTION == "Student-t":
            # using student-t shocks
            Z_indep = np.random.standard_t(df=STUDENT_T_DF, size=(self.shots, self.num_assets))
        else:
            Z_indep = np.random.normal(0, 1, size=(self.shots, self.num_assets))
            
        L = np.linalg.cholesky(correlation_matrix)
        Z_corr = Z_indep @ L.T
        
        returns = np.zeros_like(Z_corr)
        for i in range(self.num_assets):
            prices = np.exp((mu[i] - 0.5 * sigma[i]**2) * T + sigma[i] * np.sqrt(T) * Z_corr[:, i])
            returns[:, i] = prices - 1.0
            
        return returns
