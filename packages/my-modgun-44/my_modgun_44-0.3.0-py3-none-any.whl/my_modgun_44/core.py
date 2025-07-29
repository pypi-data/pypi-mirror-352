def all():
    print( """This is all the content from the module.

#lab1 fuzzy logic

import numpy as np

# --- Fuzzy Sets ---
A = np.array([0.3, 0.7, 1.0])  # Input fuzzy set
B = np.array([0.6, 0.2, 0.9])  # Output fuzzy set

# --- Fuzzy Relations ---
R = np.array([  # Relation from A to Y
    [0.2, 0.5, 0.7],
    [0.8, 0.4, 0.6],
    [0.9, 0.3, 0.5]
])

S = np.array([  # Relation from Y to B
    [0.3, 0.9, 0.6],
    [0.6, 0.7, 0.2],
    [0.5, 0.8, 0.4]
])

# --- Max-Min Composition ---
def max_min(R1, R2):
    return np.array([
        [np.max(np.minimum(R1[i], R2[:, j])) for j in range(R2.shape[1])]
        for i in range(R1.shape[0])
    ])

# --- fuzzy Implication ---
def fuzzy_implication(A, B):
    return np.array([
        [min(a, b) for b in B]
        for a in A
    ])

# --- Fuzzy Inference (A ∘ ImplicationMatrix) ---
def fuzzy_infer(A, rule_matrix):
    return np.array([
        np.max(np.minimum(A, rule_matrix[:, j]))
        for j in range(rule_matrix.shape[1])
    ])

# --- Execution ---
print("Input A:", A)
print("Output B:", B)

# 1. Max-Min Composition: R o S
RS = max_min(R, S)
print("\nMax-Min Composition (R ∘ S):\n", RS)

# 2. Fuzzy Implication Matrix: A => B
imp_matrix = fuzzy_implication(A, B)
print("\nFuzzy Implication Matrix (A ⇒ B):\n", imp_matrix)

# 3. Fuzzy Inference: A ∘ (A ⇒ B)
inferred = fuzzy_infer(A, imp_matrix)
print("\nFuzzy Inference Result:\n", inferred)





#DEFUZZIFICATION AND FUZZY CONTROLLER

import numpy as np

# --- Defuzzification Functions ---

def centroid(x, mf):
    return np.sum(x * mf) / np.sum(mf)

def mean_of_maximum(x, mf):
    max_val = np.max(mf)
    max_indices = np.where(mf == max_val)[0]
    return np.mean(x[max_indices])

# --- Fuzzy Controller ---

def fuzzy_controller(error):
    x = np.linspace(0, 100, 100)  # Output values (0-100%)

    # Fuzzy rules based on error
    if error < -5:
        output_mf = np.maximum(0, 1 - (x / 50))  # Low
    elif -5 <= error <= 5:
        output_mf = np.maximum(0, 1 - abs(x - 50) / 25)  # Medium
    else:
        output_mf = np.maximum(0, (x - 50) / 50)  # High

    # Defuzzification
    center = centroid(x, output_mf)
    mean_max = mean_of_maximum(x, output_mf)

    return center, mean_max
error = -4
centroid_output, mean_max_output = fuzzy_controller(error)

print("=== Fuzzy Controller Output ===")
print(f"Error: {error}")
print(f"Centroid Defuzzification: {centroid_output:.2f}")
print(f"Mean of Maximum: {mean_max_output:.2f}")







#GENETIC ALGORITHM

import random

POP_SIZE = 6
GENES = 5
GENERATIONS = 10

def fitness(ind):
    x = int(ind, 2)
    return x * x

def select(pop):
    return sorted(pop, key=fitness, reverse=True)[:2]

def crossover(p1, p2):
    point = random.randint(1, GENES-1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(ind):
    i = random.randint(0, GENES-1)
    return ind[:i] + str(1 - int(ind[i])) + ind[i+1:]

pop = [''.join(random.choice('01') for _ in range(GENES)) for _ in range(POP_SIZE)]

for gen in range(1, GENERATIONS + 1):
    parents = select(pop)
    offspring = []
    while len(offspring) < POP_SIZE:
        c1, c2 = crossover(*parents)
        offspring += [mutate(c1), mutate(c2)]
    pop = offspring[:POP_SIZE]

    if gen % 2 == 0:  # print every 2 generations
        best = max(pop, key=fitness)
        print(f"Generation {gen}: Best individual = {best}, x = {int(best,2)}, fitness = {fitness(best)}")

best = max(pop, key=fitness)
print("\nFinal Best individual:", best, "| x =", int(best, 2), "| f(x) =", fitness(best))








Parallel Algorithm and distributed systems (eg, Merge sort)

import concurrent.futures

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def parallel_merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    with concurrent.futures.ThreadPoolExecutor() as executor:
        left_future = executor.submit(parallel_merge_sort, arr[:mid])
        right_future = executor.submit(parallel_merge_sort, arr[mid:])
        left = left_future.result()
        right = right_future.result()

    return merge(left, right)

# Example usage:
arr = [38, 27, 43, 3, 9, 82, 10]
sorted_arr = parallel_merge_sort(arr)
print("Sorted array:", sorted_arr)

#ANT COLONY OPTIMIZATION

import numpy as np

dist = np.array([[np.inf,2,9],[1,np.inf,6],[15,7,np.inf]])
pher = np.ones_like(dist)
best_path, best_cost = None, float('inf')

for _ in range(20):
    path = [0]
    nodes = {1,2}
    while nodes:
        cur = path[-1]
        probs = [(pher[cur,j])*(1/dist[cur,j]) for j in nodes]
        probs = np.array(probs)/sum(probs)
        nxt = np.random.choice(list(nodes), p=probs)
        path.append(nxt)
        nodes.remove(nxt)
    path.append(0)
    cost = sum(dist[path[i],path[i+1]] for i in range(len(path)-1))
    if cost < best_cost:
        best_cost, best_path = cost, path
    pher *= 0.5
    for i in range(len(path)-1):
        pher[path[i], path[i+1]] += 100/cost

print("Best path:", best_path)
print("Min cost:", best_cost)






#PSO

import random

def f(x): return x*x

pos = [random.uniform(-10,10) for _ in range(5)]
vel = [0]*5
pbest = pos[:]
pbest_val = [f(x) for x in pos]
gbest = min(pbest, key=f)

for it in range(10):
    for i in range(5):
        if f(pos[i]) < pbest_val[i]:
            pbest[i] = pos[i]
            pbest_val[i] = f(pos[i])
    gbest = min(pbest, key=f)
    for i in range(5):
        vel[i] = 0.5*vel[i] + 1.5*random.random()*(pbest[i]-pos[i]) + 1.5*random.random()*(gbest-pos[i])
        pos[i] += vel[i]
    print(f"Iteration {it+1}: Best position = {gbest:.4f}, Best value = {f(gbest):.4f}")

print("\nFinal Best position:", gbest)
print("Final Best value:", f(gbest))






#grey wolf

import random

def f(x): return x*x

wolves = [random.uniform(-10, 10) for _ in range(5)]
a = 2

for iter in range(10):
    wolves.sort(key=f)
    alpha, beta, delta = wolves[0], wolves[1], wolves[2]
    a -= 2 / 10
    new_wolves = []
    for w in wolves:
        r1, r2 = random.random(), random.random()
        A = 2 * a * r1 - a
        C = 2 * r2
        D_alpha = abs(C * alpha - w)
        X1 = alpha - A * D_alpha

        r1, r2 = random.random(), random.random()
        A = 2 * a * r1 - a
        C = 2 * r2
        D_beta = abs(C * beta - w)
        X2 = beta - A * D_beta

        r1, r2 = random.random(), random.random()
        A = 2 * a * r1 - a
        C = 2 * r2
        D_delta = abs(C * delta - w)
        X3 = delta - A * D_delta

        new_wolves.append((X1 + X2 + X3) / 3)
    wolves = new_wolves
    print(f"Iter {iter+1}: Best = {alpha:.4f}, Value = {f(alpha):.4f}")

print(f"Best solution: {alpha:.4f} with value: {f(alpha):.4f}")



#Crisp Partitions for real-life iris dataset

from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import numpy as np

# Load Iris dataset
iris = load_iris()
X = iris.data  # features

# Number of clusters (species)
k = 3

# Apply KMeans clustering
kmeans = KMeans(n_clusters=k, random_state=0)
kmeans.fit(X)

# Cluster assignments (crisp partition)
labels = kmeans.labels_

# Display results
for i in range(k):
    cluster_points = X[labels == i]
    print(f"Cluster {i+1} has {len(cluster_points)} points.")
    print(cluster_points[:3], "...")  # print first 3 points in cluster

# Optional: Show cluster centers
print("\nCluster Centers:")
print(kmeans.cluster_centers_)





#perceptron hebb's rule

import numpy as np

# Inputs (4 samples, 2 features)
X = np.array([[0,0], [0,1], [1,0], [1,1]])
# Targets (AND logic)
y = np.array([0, 0, 0, 1])

# Initialize weights and bias
w = np.zeros(2)
b = 0

def activation(x):
    return 1 if x > 0 else 0

epochs = 5

for epoch in range(epochs):
    for xi, target in zip(X, y):
        output = activation(np.dot(w, xi) + b)
        error = target - output
        # Hebb's Rule update only if target is 1 (reinforcement)
        if target == 1:
            w += xi
            b += 1
    print(f"Epoch {epoch+1}: Weights = {w}, Bias = {b}")

print("\nFinal Weights:", w)
print("Final Bias:", b)






#delta rule
import numpy as np

# Inputs (4 samples, 2 features)
X = np.array([[0,0], [0,1], [1,0], [1,1]])
# Targets (AND logic)
y = np.array([0, 0, 0, 1])

# Initialize weights and bias
w = np.zeros(2)
b = 0
lr = 0.1  # learning rate

def activation(x):
    # Linear output (no threshold, as delta rule works with continuous values)
    return x

epochs = 10

for epoch in range(epochs):
    for xi, target in zip(X, y):
        output = activation(np.dot(w, xi) + b)
        error = target - output
        w += lr * error * xi
        b += lr * error
    print(f"Epoch {epoch+1}: Weights = {w}, Bias = {b}")

print("\nFinal Weights:", w)
print("Final Bias:", b)





#ensemble

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Bagging with random features and shallow trees
bag = BaggingClassifier(
    estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=5,
    max_samples=0.5,
    max_features=0.5,
    random_state=42
)

# Train
bag.fit(X_train, y_train)

# Test sample
sample = X_test[0].reshape(1, -1)
print("True label:", y_test[0])
print("Individual Estimator Predictions:")
for i, est in enumerate(bag.estimators_):
    feats = bag.estimators_features_[i]
    print(f"Model {i+1}: {est.predict(sample[:, feats])[0]}")

# Bagging prediction
print("Bagging Final Prediction:", bag.predict(sample)[0])

    """)
