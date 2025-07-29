"""
Core functionality for the Code Printer package
"""

class CodePrinter:
    def __init__(self):
        # Your set of 12 codes - now including your ML algorithm
        self.codes = {
            1: """import numpy as np
import pandas as pd

# Candidate Elimination Algorithm
data = pd.read_csv("enjoysport.csv")
concepts = np.array(data.iloc[:, 0:-1])
print("\\nInstances are:\\n", concepts)
target = np.array(data.iloc[:, -1])
print("\\nTarget Values are: ", target)

def learn(concepts, target):
    positive_instances = [concepts[i] for i in range(len(concepts)) if target[i] == 'yes']
    specific_h = positive_instances[0].copy()
    print("\\nInitialization of specific_h and generic_h")
    print("\\nSpecific Boundary: ", specific_h)
    general_h = [['?' for _ in range(len(specific_h))] for _ in range(len(specific_h))]
    print("\\nGeneric Boundary: ", general_h)
    
    for i, h in enumerate(concepts):
        print("\\nInstance", i + 1, "is ", h)
        if target[i] == "yes":
            print("Instance is Positive ")
            for x in range(len(specific_h)):
                if h[x] != specific_h[x]:
                    specific_h[x] = '?'
                general_h[x][x] = '?'
        if target[i] == "no":
            print("Instance is Negative ")
            for x in range(len(specific_h)):
                if h[x] != specific_h[x]:
                    general_h[x][x] = specific_h[x]
                else:
                    general_h[x][x] = '?'
        print("Specific Boundary after ", i + 1, "Instance is ", specific_h)
        print("Generic Boundary after ", i + 1, "Instance is ", general_h)
        print("\\n")
    
    # Clean up redundant hypotheses
    indices = [i for i, val in enumerate(general_h) if val == ['?' for _ in range(len(specific_h))]]
    for i in indices:
        general_h.remove(['?' for _ in range(len(specific_h))])
    return specific_h, general_h

s_final, g_final = learn(concepts, target)
print("Final Specific_h: ", s_final, sep="\\n")
print("Final General_h: ", g_final, sep="\\n")""",

            2: """# Linear Regression from Scratch
import numpy as np
import matplotlib.pyplot as plt

def linear_regression(X, y, learning_rate=0.01, epochs=1000):
    m, n = X.shape
    theta = np.zeros(n)
    
    for epoch in range(epochs):
        predictions = X.dot(theta)
        errors = predictions - y
        gradient = (1/m) * X.T.dot(errors)
        theta -= learning_rate * gradient
        
        if epoch % 100 == 0:
            cost = (1/(2*m)) * np.sum(errors**2)
            print(f'Epoch {epoch}, Cost: {cost}')
    
    return theta""",

            3: """# K-Means Clustering Implementation
import numpy as np
import matplotlib.pyplot as plt

def kmeans(X, k, max_iters=100):
    centroids = X[np.random.choice(X.shape[0], k, replace=False)]
    
    for _ in range(max_iters):
        distances = np.sqrt(((X - centroids[:, np.newaxis])**2).sum(axis=2))
        labels = np.argmin(distances, axis=0)
        
        new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])
        
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids
    
    return labels, centroids""",

            4: """# Decision Tree Node Implementation
class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
    
    def is_leaf(self):
        return self.value is not None

def gini_impurity(y):
    classes, counts = np.unique(y, return_counts=True)
    probabilities = counts / len(y)
    return 1 - np.sum(probabilities ** 2)

def information_gain(y, y_left, y_right):
    p = len(y_left) / len(y)
    return gini_impurity(y) - p * gini_impurity(y_left) - (1 - p) * gini_impurity(y_right)""",

            5: """# Neural Network Forward Pass
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def relu(x):
    return np.maximum(0, x)

class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.weights = []
        self.biases = []
        
        for i in range(len(layers) - 1):
            w = np.random.randn(layers[i], layers[i+1]) * 0.1
            b = np.zeros((1, layers[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def forward(self, X):
        activation = X
        for w, b in zip(self.weights, self.biases):
            z = np.dot(activation, w) + b
            activation = sigmoid(z)
        return activation""",

            6: """# Support Vector Machine (SVM) Implementation
import numpy as np

class SVM:
    def __init__(self, learning_rate=0.001, lambda_param=0.01, n_iters=1000):
        self.lr = learning_rate
        self.lambda_param = lambda_param
        self.n_iters = n_iters
        self.w = None
        self.b = None
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        y_ = np.where(y <= 0, -1, 1)
        
        self.w = np.zeros(n_features)
        self.b = 0
        
        for i in range(self.n_iters):
            for idx, x_i in enumerate(X):
                condition = y_[idx] * (np.dot(x_i, self.w) - self.b) >= 1
                if condition:
                    self.w -= self.lr * (2 * self.lambda_param * self.w)
                else:
                    self.w -= self.lr * (2 * self.lambda_param * self.w - np.dot(x_i, y_[idx]))
                    self.b -= self.lr * y_[idx]""",

            7: """# Random Forest Implementation
import numpy as np
from collections import Counter

class RandomForest:
    def __init__(self, n_trees=10, max_depth=10, min_samples_split=2, n_features=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_features = n_features
        self.trees = []
    
    def fit(self, X, y):
        self.trees = []
        for _ in range(self.n_trees):
            tree = DecisionTree(max_depth=self.max_depth, 
                              min_samples_split=self.min_samples_split,
                              n_features=self.n_features)
            X_sample, y_sample = self._bootstrap_samples(X, y)
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)
    
    def _bootstrap_samples(self, X, y):
        n_samples = X.shape[0]
        idxs = np.random.choice(n_samples, n_samples, replace=True)
        return X[idxs], y[idxs]
    
    def predict(self, X):
        predictions = np.array([tree.predict(X) for tree in self.trees])
        tree_preds = np.swapaxes(predictions, 0, 1)
        predictions = np.array([self._most_common_label(pred) for pred in tree_preds])
        return predictions""",

            8: """# Gradient Descent Optimization
import numpy as np
import matplotlib.pyplot as plt

def gradient_descent(X, y, learning_rate=0.01, epochs=1000, verbose=True):
    m, n = X.shape
    theta = np.random.randn(n)
    cost_history = []
    
    for epoch in range(epochs):
        # Forward pass
        predictions = X.dot(theta)
        
        # Compute cost
        cost = (1/(2*m)) * np.sum((predictions - y)**2)
        cost_history.append(cost)
        
        # Compute gradients
        gradients = (1/m) * X.T.dot(predictions - y)
        
        # Update parameters
        theta -= learning_rate * gradients
        
        if verbose and epoch % 100 == 0:
            print(f'Epoch {epoch}: Cost = {cost:.6f}')
    
    return theta, cost_history""",

            9: """# Principal Component Analysis (PCA)
import numpy as np

def pca(X, n_components):
    # Center the data
    X_centered = X - np.mean(X, axis=0)
    
    # Compute covariance matrix
    cov_matrix = np.cov(X_centered.T)
    
    # Compute eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # Sort eigenvalues and eigenvectors in descending order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Select top n_components
    components = eigenvectors[:, :n_components]
    
    # Transform the data
    X_transformed = X_centered.dot(components)
    
    # Calculate explained variance ratio
    explained_variance_ratio = eigenvalues[:n_components] / np.sum(eigenvalues)
    
    return X_transformed, components, explained_variance_ratio""",

            10: """# Logistic Regression Implementation
import numpy as np

class LogisticRegression:
    def __init__(self, learning_rate=0.01, max_iterations=1000):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.weights = None
        self.bias = None
    
    def sigmoid(self, z):
        z = np.clip(z, -250, 250)  # Prevent overflow
        return 1 / (1 + np.exp(-z))
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for i in range(self.max_iterations):
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)
            
            cost = self.compute_cost(y, y_predicted)
            
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1 / n_samples) * np.sum(y_predicted - y)
            
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
    
    def compute_cost(self, y_true, y_pred):
        cost = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        return cost""",

            11: """# Naive Bayes Classifier
import numpy as np

class NaiveBayes:
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self._classes = np.unique(y)
        n_classes = len(self._classes)
        
        # Calculate mean, var, and prior for each class
        self._mean = np.zeros((n_classes, n_features), dtype=np.float64)
        self._var = np.zeros((n_classes, n_features), dtype=np.float64)
        self._priors = np.zeros(n_classes, dtype=np.float64)
        
        for idx, c in enumerate(self._classes):
            X_c = X[y == c]
            self._mean[idx, :] = X_c.mean(axis=0)
            self._var[idx, :] = X_c.var(axis=0)
            self._priors[idx] = X_c.shape[0] / float(n_samples)
    
    def predict(self, X):
        y_pred = [self._predict(x) for x in X]
        return np.array(y_pred)
    
    def _predict(self, x):
        posteriors = []
        
        for idx, c in enumerate(self._classes):
            prior = np.log(self._priors[idx])
            posterior = np.sum(np.log(self._pdf(idx, x)))
            posterior = prior + posterior
            posteriors.append(posterior)
        
        return self._classes[np.argmax(posteriors)]
    
    def _pdf(self, class_idx, x):
        mean = self._mean[class_idx]
        var = self._var[class_idx]
        numerator = np.exp(-((x - mean) ** 2) / (2 * var))
        denominator = np.sqrt(2 * np.pi * var)
        return numerator / denominator""",

            12: """# K-Nearest Neighbors (KNN) Implementation
import numpy as np
from collections import Counter

class KNN:
    def __init__(self, k=3):
        self.k = k
    
    def fit(self, X, y):
        self.X_train = X
        self.y_train = y
    
    def predict(self, X):
        y_pred = [self._predict(x) for x in X]
        return np.array(y_pred)
    
    def _predict(self, x):
        # Compute distances between x and all examples in the training set
        distances = [self._euclidean_distance(x, x_train) for x_train in self.X_train]
        
        # Sort by distance and return indices of the first k neighbors
        k_idx = np.argsort(distances)[:self.k]
        
        # Extract the labels of the k nearest neighbor training samples
        k_neighbor_labels = [self.y_train[i] for i in k_idx]
        
        # Return the most common class label
        most_common = Counter(k_neighbor_labels).most_common(1)
        return most_common[0][0]
    
    def _euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2))"""
        }
    
    def print_code(self, code_number):
        """Print a specific code by number"""
        if code_number in self.codes:
            print(f"🤖 Machine Learning Code #{code_number}:")
            print("=" * 60)
            print(self.codes[code_number])
            print("=" * 60)
            return True
        else:
            print(f"❌ Error: Code #{code_number} not found.")
            print(f"Available codes: {', '.join(map(str, sorted(self.codes.keys())))}")
            return False
    
    def print_all_codes(self):
        """Print all codes"""
        print("🤖 All Machine Learning Algorithms:")
        print("=" * 70)
        algorithm_names = [
            "Candidate Elimination Algorithm",
            "Linear Regression from Scratch", 
            "K-Means Clustering",
            "Decision Tree Node",
            "Neural Network Forward Pass",
            "Support Vector Machine (SVM)",
            "Random Forest",
            "Gradient Descent Optimization",
            "Principal Component Analysis (PCA)",
            "Logistic Regression",
            "Naive Bayes Classifier",
            "K-Nearest Neighbors (KNN)"
        ]
        
        for num in sorted(self.codes.keys()):
            print(f"\n🔢 Code #{num}: {algorithm_names[num-1]}")
            print("-" * 60)
            print(self.codes[num])
            print("-" * 60)
    
    def list_codes(self):
        """List all available code numbers with previews"""
        print("🤖 Available Machine Learning Algorithms:")
        print("=" * 70)
        algorithm_names = [
            "Candidate Elimination Algorithm",
            "Linear Regression from Scratch", 
            "K-Means Clustering",
            "Decision Tree Node Implementation",
            "Neural Network Forward Pass",
            "Support Vector Machine (SVM)",
            "Random Forest Implementation",
            "Gradient Descent Optimization",
            "Principal Component Analysis (PCA)",
            "Logistic Regression Implementation",
            "Naive Bayes Classifier",
            "K-Nearest Neighbors (KNN)"
        ]
        
        for num in sorted(self.codes.keys()):
            print(f"  {num:2d}: {algorithm_names[num-1]}")
        print("=" * 70)
        print("💡 Use 'code-printer <number>' to view a specific algorithm")
        print("💡 Use 'code-printer --all' to view all algorithms")
    
    def search_codes(self, keyword):
        """Search for codes containing a keyword"""
        matches = []
        algorithm_names = [
            "Candidate Elimination Algorithm",
            "Linear Regression from Scratch", 
            "K-Means Clustering",
            "Decision Tree Node Implementation",
            "Neural Network Forward Pass",
            "Support Vector Machine (SVM)",
            "Random Forest Implementation",
            "Gradient Descent Optimization",
            "Principal Component Analysis (PCA)",
            "Logistic Regression Implementation",
            "Naive Bayes Classifier",
            "K-Nearest Neighbors (KNN)"
        ]
        
        for num, code in self.codes.items():
            if (keyword.lower() in code.lower() or 
                keyword.lower() in algorithm_names[num-1].lower()):
                matches.append((num, algorithm_names[num-1]))
        
        if matches:
            print(f"🔍 Found {len(matches)} algorithm(s) matching '{keyword}':")
            print("=" * 70)
            for num, name in matches:
                print(f"  {num:2d}: {name}")
        else:
            print(f"❌ No algorithms found matching '{keyword}'")

# Test the functionality
if __name__ == "__main__":
    printer = CodePrinter()
    
    print("🤖 Machine Learning Code Printer Demo")
    print("=" * 50)
    
    print("\n📋 Available algorithms:")
    printer.list_codes()
    
    print(f"\n🔍 Searching for 'regression':")
    printer.search_codes("regression")
    
    print(f"\n📄 Showing Code #1 (Your Candidate Elimination Algorithm):")
    printer.print_code(1)