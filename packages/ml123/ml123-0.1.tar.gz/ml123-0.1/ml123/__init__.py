p1='''import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
df = fetch_california_housing(as_frame=True).frame
a = df.select_dtypes(include=[np.number]).columns
for col in a:
    sns.histplot(df[col], kde=True)
    plt.title(col)
    plt.show()
    sns.boxplot(x=df[col])
    plt.title(col)
    plt.show()
for col in a:
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
    print(f"{col}: {len(outliers)} outliers")
print(df.describe())'''
p2='''import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
df = fetch_california_housing(as_frame=True).frame
corr = df.corr()
plt.figure(figsize=(10,8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix of Features')
plt.show()
sns.pairplot(df[df.columns[:5]], plot_kws={'alpha':0.7})
plt.suptitle('Pair Plot of Selected Features', y=1.02)
plt.show()'''

p3='''import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
iris = load_iris()
X = iris.data
y = iris.target
X_scaled = StandardScaler().fit_transform(X)
X_pca = PCA(n_components=2).fit_transform(X_scaled)
plt.scatter(X_pca[:,0], X_pca[:,1], c=y, cmap='viridis', edgecolor='k', s=50)
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA - Iris Dataset (Reduced to 2 Dimensions)')
plt.colorbar(label='Iris Species')
plt.show()
print('Explained variance ratio for each component:', PCA(n_components=2).fit(X_scaled).explained_variance_ratio_)'''

p4='''import pandas as pd
def find_s_algorithm(file_path):
    data = pd.read_csv(file_path)
    print("Training data:")
    print(data)
    attributes = data.columns[:-1]
    class_label = data.columns[-1]
    hypothesis = ['?' for _ in attributes]
    for _, row in data.iterrows():
        if row[class_label] == 'Yes':
            for i, value in enumerate(row[attributes]):
                if hypothesis[i] == '?' or hypothesis[i] == value:
                    hypothesis[i] = value
                else:
                    hypothesis[i] = '?'
    return hypothesis
file_path = 'training_data.csv'
hypothesis = find_s_algorithm(file_path)
print("\nThe final hypothesis is:", hypothesis)'''

p5='''import numpy as np, matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
np.random.seed(42)
X = np.random.rand(100,1)
y = np.array([1 if x <= 0.5 else 2 for x in X[:50]] + [0]*50)
X_train, X_test = X[:50], X[50:]
y_train = y[:50]
k_values = [1,2,3,4,5,20,30]
accuracies = []
for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    acc = accuracy_score(y[50:], y_pred)
    accuracies.append(acc)
    print(f"Accuracy for k={k}: {acc:.4f}")
plt.scatter(X_train, y_train, color='blue', label='Training Data')
plt.scatter(X_test, y[50:], color='red', label='Test Data')
plt.xlabel('X values')
plt.ylabel('Classes')
plt.title('k-NN Classification for Randomly Generated Data')
plt.legend()
plt.show()'''
p6='''import numpy as np
import matplotlib.pyplot as plt

def locally_weighted_regression(X_train, Y_train, X_query, tau=0.1):
    m, n = X_train.shape
    Y_train = Y_train.reshape(-1, 1)
    X_train = np.concatenate([np.ones((m, 1)), X_train], axis=1)
    X_query = np.concatenate([np.ones((X_query.shape[0], 1)), X_query], axis=1)
    Y_pred = np.zeros(X_query.shape[0])
    for i in range(X_query.shape[0]):
        weights = np.exp(-np.sum((X_train - X_query[i])**2, axis=1) / (2 * tau**2))
        W = np.diag(weights)
        theta = np.linalg.inv(X_train.T @ W @ X_train) @ (X_train.T @ W @ Y_train)
        Y_pred[i] = X_query[i] @ theta
    return Y_pred

np.random.seed(42)
X = np.sort(np.random.rand(100, 1), axis=0)
Y = np.sin(2 * np.pi * X) + 0.1 * np.random.randn(100, 1)
X_query = np.linspace(0, 1, 100).reshape(-1, 1)
tau_values = [0.1, 0.3, 0.5, 1.0, 2.0]
plt.figure(figsize=(10, 6))
for tau in tau_values:
    Y_pred = locally_weighted_regression(X, Y, X_query, tau)
    plt.plot(X_query, Y_pred, label=f'tau={tau}')
plt.scatter(X, Y, color='red', label='Data points')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Locally Weighted Regression')
plt.legend()
plt.show()'''
p7='''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score

def linear_regression_california():
    housing = fetch_california_housing(as_frame=True)
    X = housing.data[["AveRooms"]]
    y = housing.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    plt.scatter(X_test, y_test, color="blue", label="Actual")
    plt.plot(X_test, y_pred, color="red", label="Predicted")
    plt.xlabel("AveRooms")
    plt.ylabel("Median value")
    plt.title("Linear Regression - California Housing")
    plt.legend()
    plt.show()
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("R^2:", r2_score(y_test, y_pred))

def polynomial_regression_auto_mpg():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
    column_names = ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year", "origin"]
    data = pd.read_csv(url, sep='\s+', names=column_names, na_values="?")
    data = data.dropna()
    X = data["displacement"].values.reshape(-1, 1)
    y = data["mpg"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    poly_model = make_pipeline(PolynomialFeatures(degree=2), StandardScaler(), LinearRegression())
    poly_model.fit(X_train, y_train)
    y_pred = poly_model.predict(X_test)
    plt.scatter(X_test, y_test, color="blue", label="Actual")
    plt.scatter(X_test, y_pred, color="red", label="Predicted")
    plt.xlabel("Displacement")
    plt.ylabel("MPG")
    plt.title("Polynomial Regression - Auto MPG")
    plt.legend()
    plt.show()
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("R^2:", r2_score(y_test, y_pred))

linear_regression_california()
polynomial_regression_auto_mpg()'''

p8='''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, classification_report

data = load_breast_cancer()
X = data.data
y = data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(classification_report(y_test, y_pred))
plt.figure(figsize=(12, 8))
plot_tree(clf, filled=True, feature_names=data.feature_names, class_names=data.target_names, rounded=True)
plt.title("Decision Tree Visualized")
plt.show()
new_sample = np.array([[15.2, 19.5, 103.2, 800.2, 0.07, 0.3, 1.2, 4.2, 0.03, 0.1, 0.08, 0.05, 0.03, 0.03, 0.06,
    0.09, 0.02, 0.07, 0.03, 0.08, 0.04, 0.02, 0.01, 0.04, 0.06, 0.03, 0.02, 0.01, 0.03, 0.02]])
print("New sample classified as:", data.target_names[clf.predict(new_sample)][0])'''

p9='''import numpy as np
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt

data = fetch_olivetti_faces(shuffle=True, random_state=42)
X = data.data
y = data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
gnb = GaussianNB()
gnb.fit(X_train, y_train)
y_pred = gnb.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%')
print(classification_report(y_test, y_pred, zero_division=1))
print(confusion_matrix(y_test, y_pred))
cv_score = cross_val_score(gnb, X, y, cv=5, scoring='accuracy')
print(f'Cross-validation accuracy: {cv_score.mean() * 100:.2f}%')
fig, axes = plt.subplots(3, 5, figsize=(12, 8))
for ax, img, true, pred in zip(axes.ravel(), X_test, y_test, y_pred):
    ax.imshow(img.reshape(64, 64), cmap='gray')
    ax.set_title(f'True: {true}, Pred: {pred}')
    ax.axis('off')
plt.show()'''
p10='''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

data = load_breast_cancer()
X = data.data
y = data.target
X_scaled = StandardScaler().fit_transform(X)
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(X_scaled)
X_pca = PCA(n_components=2).fit_transform(X_scaled)
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[clusters == 0, 0], X_pca[clusters == 0, 1], s=50, c='red', label='Cluster 0')
plt.scatter(X_pca[clusters == 1, 0], X_pca[clusters == 1, 1], s=50, c='blue', label='Cluster 1')
centroids = PCA(n_components=2).fit_transform(kmeans.cluster_centers_)
plt.scatter(centroids[:, 0], centroids[:, 1], s=200, c='black', marker='X', label='Centroids')
plt.title('K-Means Clustering on Breast Cancer Dataset')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()
plt.show()''''''
