"""
Core functionality for the Code Printer package
"""

class CodePrinter:
    def __init__(self):
        #set of 10 codes 
        self.codes = {
            1: """#Find-S algorithm
            import numpy as np
import pandas as pd
data = pd.read_csv("enjoysport.csv")

concepts = np.array(data.iloc[:, 0:-1])
target = np.array(data.iloc[:, -1])

print("\nInstances are:\n", concepts)
print("\nTarget Values are:\n", target)

# Find-S Algorithm
def find_s(concepts, target):

    for i, val in enumerate(target):
        if val == "yes":
            specific_h = concepts[i].copy()
            break

    print("\nInitial Specific Hypothesis:\n", specific_h)

    for i, val in enumerate(concepts):
        if target[i] == "yes":
            for x in range(len(specific_h)):
                if val[x] != specific_h[x]:
                    specific_h[x] = '?'

    return specific_h


final_hypothesis = find_s(concepts, target)
print("\nFinal Specific Hypothesis:\n", final_hypothesis)
""",
            2: """# Candidate Elimination Algorithm
import numpy as np
import pandas as pd

data = pd.read_csv("enjoysport.csv")
concepts = np.array(data.iloc[:, 0:-1])
target = np.array(data.iloc[:, -1])

print("\nInstances are:\n", concepts)
print("\nTarget Values are:\n", target)

def learn(concepts, target):

    specific_h = concepts[0].copy()
    general_h = [["?" for _ in range(len(specific_h))] for _ in range(len(specific_h))]

    print("\nInitialization of specific_h and general_h")
    print("\nSpecific Boundary:", specific_h)
    print("\nGeneric Boundary:", general_h)


    for i, h in enumerate(concepts):
        print("\nInstance", i + 1, "is", h)
        
        if target[i] == "yes":
            print("Instance is Positive")
            for x in range(len(specific_h)):
                if h[x] != specific_h[x]:
                    specific_h[x] = '?'
                    general_h[x][x] = '?'
        elif target[i] == "no":
            print("Instance is Negative")
            for x in range(len(specific_h)):
                if h[x] != specific_h[x]:
                    general_h[x][x] = specific_h[x]
                else:
                    general_h[x][x] = '?'

        print("Specific Boundary after", i + 1, "Instance is", specific_h)
        print("Generic Boundary after", i + 1, "Instance is", general_h)


    general_h = [h for h in general_h if h != ["?" for _ in range(len(specific_h))]]

    return specific_h, general_h


s_final, g_final = learn(concepts, target)

print("\nFinal Specific Hypothesis:\n", s_final)
print("\nFinal General Hypothesis:\n", g_final)
""",

            3: """#ID3 Algorithm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score


data = pd.read_csv("/content/archive (2).zip")

print("Class Distribution in Diagnosis Column:\n")
print(data["diagnosis"].value_counts())


label_encode = preprocessing.LabelEncoder()
labels = label_encode.fit_transform(data["diagnosis"])
data["target"] = labels
data.drop(columns="diagnosis", axis=1, inplace=True)


X = data.iloc[:, :-1]
y = data.iloc[:, -1]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

classifier = DecisionTreeClassifier(criterion='entropy', random_state=0)
classifier.fit(X_train, y_train)


y_pred = classifier.predict(X_test)


cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:\n", cm)


print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nAccuracy Score:", accuracy_score(y_test, y_pred))


feature_importances = classifier.feature_importances_
plt.barh(X.columns, feature_importances)
plt.title("Feature Importances")
plt.show()
""",

            4: """#Support Vector Machine
import numpy as np
import pandas as pd
from sklearn import svm


iris = pd.read_csv('iris.csv')
X = iris.iloc[:, :-1]
y = iris.iloc[:, -1]


from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)


clf = svm.SVC(kernel='rbf')
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy with RBF kernel:', accuracy)

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = SVC(kernel='linear')
clf.fit(X_train, y_train)

predictions = clf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print("Accuracy with Linear kernel:", accuracy)
""",

            5: """#k-nearest neighbour
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt

irisData = load_iris()

X = irisData.data
y = irisData.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))


for i, k in enumerate(neighbors):

    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    train_accuracy[i] = knn.score(X_train, y_train)
    
   
    test_accuracy[i] = knn.score(X_test, y_test)


plt.plot(neighbors, test_accuracy, label='Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label='Training dataset Accuracy')
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.title('KNN varying number of neighbors')
plt.show()
""",

            6: """
#EM Algorithm
import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
import seaborn as sns

mu1, sigma1 = 2, 1
mu2, sigma2 = -1, 0.8
X1 = np.random.normal(mu1, sigma1, size=200)
X2 = np.random.normal(mu2, sigma2, size=600)

X = np.concatenate([X1, X2])
X = X.reshape(-1, 1)

gmm = GaussianMixture(n_components=2, random_state=0)
gmm.fit(X)

x_grid = np.linspace(min(X), max(X), 1000).reshape(-1, 1)

density_estimation = np.exp(gmm.score_samples(x_grid))

sns.kdeplot(X.flatten(), label="Actual Density")
plt.plot(x_grid, density_estimation, label='Estimated density\nFrom Gaussian Mixture Model')
plt.xlabel('X')
plt.ylabel('Density')
plt.title('Density Estimation using GMM')
plt.legend()
plt.show()
""",

            7: """# Naive Bayes Classifier
from sklearn.model_selection import train_test_split  
from sklearn.naive_bayes import CategoricalNB          
from sklearn.metrics import accuracy_score, classification_report  
import pandas as pd                                    

data = {
    'Feature1': [1, 2, 2, 1, 3, 3, 1, 2, 3, 3],
    'Feature2': ['A', 'B', 'B', 'A', 'C', 'C', 'A', 'B', 'C', 'C'],
    'Class': [0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
}
df = pd.DataFrame(data)


df_encoded = pd.get_dummies(df, columns=['Feature2'])

X_train, X_test, y_train, y_test = train_test_split(
    df_encoded.drop('Class', axis=1), df['Class'], test_size=0.2, random_state=42
)
nb_classifier = CategoricalNB()
nb_classifier.fit(X_train, y_train)
y_pred = nb_classifier.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')

print('Classification Report:')
print(classification_report(y_test, y_pred))
""",

            8: """#KMEANS ALGORITHM
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import datasets

iris = datasets.load_iris()
X = iris.data

inertia = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
    kmeans.fit(X)
    inertia.append(kmeans.inertia_)


plt.plot(range(1, 11), inertia, marker='o')
plt.title('Elbow Method for Optimal K')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Inertia')
plt.show()


kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, n_init=10, random_state=42)
kmeans.fit(X)


labels = kmeans.labels_
centroids = kmeans.cluster_centers_


plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', edgecolors='k')
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
plt.title('K-means Clustering of Iris Dataset')
plt.xlabel('Sepal Length (cm)')
plt.ylabel('Sepal Width (cm)')
plt.legend()
plt.show()
""",

            9: """# Apriori Algorithm
from itertools import combinations
def generate_C1(dataset):
    C1 = set()
    for transaction in dataset:
        for item in transaction:
            C1.add(frozenset([item]))
    return C1

def generate_L1(dataset, C1, min_support):
    item_count = {}
    for transaction in dataset:
        for item in transaction:
            item_count[frozenset([item])] = item_count.get(frozenset([item]), 0) + 1
    L1 = {itemset for itemset, count in item_count.items() if count >= min_support}
    return L1, item_count

def generate_Ck(Lk_minus_1, k):
    Ck = set()
    for itemset1 in Lk_minus_1:
        for itemset2 in Lk_minus_1:
            union_set = itemset1.union(itemset2)
            if len(union_set) == k:
                Ck.add(union_set)
    return Ck

def generate_Lk(dataset, Ck, min_support):
    item_count = {}
    for transaction in dataset:
        for itemset in Ck:
            if itemset.issubset(transaction):
                item_count[itemset] = item_count.get(itemset, 0) + 1
    Lk = {itemset for itemset, count in item_count.items() if count >= min_support}
    return Lk, item_count


def apriori(dataset, min_support):
    C1 = generate_C1(dataset)
    L1, item_count = generate_L1(dataset, C1, min_support)
    L = [L1]
    k = 2
    while len(L[k-2]) > 0:
        Ck = generate_Ck(L[k-2], k)
        Lk, item_count = generate_Lk(dataset, Ck, min_support)
        L.append(Lk)
        k += 1
    return L, item_count


dataset = [['bread', 'milk'],
           ['bread', 'diaper', 'beer', 'egg'],
           ['milk', 'diaper', 'beer', 'cola'],
           ['bread', 'milk', 'diaper', 'beer'],
           ['bread', 'milk', 'diaper', 'cola']]

min_support = 3  

frequent_itemsets, item_count = apriori(dataset, min_support)

for k, Lk in enumerate(frequent_itemsets):
    print(f"Frequent {k+1}-itemsets:")
    print(Lk)
    print()
""",

            10: """#PCA-PRINCIPAL COMPONENT ANALYSIS
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

iris = load_iris()
X = iris.data
y = iris.target

X_std = StandardScaler().fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_std)

plt.figure(figsize=(8, 6))
for i in range(len(iris.target_names)):
    plt.scatter(X_pca[y == i, 0], X_pca[y == i, 1], label=iris.target_names[i])
plt.title('PCA on Iris Dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.show()
"""
        }
    
    def print(self, code_number):
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
            "Find S Algorithm",
            "Candidate Elimination Algorithm",
            "ID3 Algorithm", 
            "SVM Support Vector Machine",
            "K- Nearest Neighbor algorithm",
            "EM Algorithm",
            "Naïve bayes Classifier",
            "K-Means Algorithm",
            "Apriori Algorithm",
            "Principal Component Analysis PCA"
            
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
            "Find S Algorithm",
            "Candidate Elimination Algorithm",
            "ID3 Algorithm", 
            "SVM Support Vector Machine",
            "K- Nearest Neighbor algorithm",
            "EM Algorithm",
            "Naïve bayes Classifier",
            "K-Means Algorithm",
            "Apriori Algorithm",
            "Principal Component Analysis PCA"
        ]
        
        for num in sorted(self.codes.keys()):
            print(f"  {num:2d}: {algorithm_names[num-1]}")
        print("=" * 70)
        print("💡 Use 'code-printer <number>' to view a specific algorithm")
        print("💡 Use 'code-printer --all' to view all algorithms")
    
    def search(self, keyword):
        """Search for codes containing a keyword"""
        matches = []
        algorithm_names = [
            "Find S Algorithm",
            "Candidate Elimination Algorithm",
            "ID3 Algorithm", 
            "SVM Support Vector Machine",
            "K- Nearest Neighbor algorithm",
            "EM Algorithm",
            "Naïve bayes Classifier",
            "K-Means Algorithm",
            "Apriori Algorithm",
            "Principal Component Analysis PCA"
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