def print_ml_programs(indx):
    mlprogs=[ """#LAB1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#load dataset
df = pd.read_csv('tested.xls')

#select one numerical column
numerical_column = 'Owner_Count'
data = df[numerical_column]

#compute statistical measures
mean_value = data.mean()
median_value = data.median()
mode_value = data.mode()[0]
std_dev = data.std()
variance = data.var()
data_range = data.max() - data.min()

print(f'Mean: {mean_value}')
print(f'Median: {median_value}')
print(f'Mode: {mode_value}')
print(f'Standard deviation: {std_dev}')
print(f'Variance: {variance}')
print(f'Range: {data_range}')

#generate histogram
plt.figure(figsize=(10,6))
sns.histplot(data, kde=True)
plt.title('Histogram of '+numerical_column)
plt.xlabel(numerical_column)
plt.ylabel('Frequency')
plt.show()

#generate boxplot
plt.figure(figsize=(10,6))
sns.boxplot(x=data)
plt.title('Boxplot of '+numerical_column)
plt.show()

# Identify outliers using IQR
Q1 = data.quantile(0.25)
Q3 = data.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = data[(data < lower_bound) | (data > upper_bound)]
print(f'Outliers: {outliers}')

# Select a categorical variable
categorical_column = 'Brand'  # Replace with your categorical column name
category_counts = df[categorical_column].value_counts()
print(category_counts)

# Display as bar chart
plt.figure(figsize=(10, 6))
sns.barplot(x=category_counts.index, y=category_counts.values)
plt.title('Bar Chart of ' + categorical_column)
plt.xlabel(categorical_column)
plt.ylabel('Frequency')
plt.show()

# Display as pie chart
plt.figure(figsize=(10, 6))
category_counts.plot.pie(autopct='%1.1f%%')
plt.title('Pie Chart of ' + categorical_column)
plt.ylabel('')
plt.show()
""",
"""#LAB2

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import datasets

# Load the Iris dataset
iris = datasets.load_iris()

X=iris.data
y=iris.feature_names

# Convert data to a DataFrame
df = pd.DataFrame(data=X, columns=y)

# Select columns for scatter plot
x_column = 'sepal length (cm)'
y_column = 'sepal width (cm)'

#plot scatter plot
plt.figure(figsize=(8,6))
plt.scatter(df[x_column], df[y_column], color='b', alpha=0.5)
plt.title(f'Scatter plot of {x_column} vs {y_column}')
plt.xlabel(x_column)
plt.ylabel(y_column)
plt.show()

#calculate pearson correlation coefficient
pearson= df[x_column].corr(df[y_column])
print(f'Pearson correlation coefficient between {x_column} and {y_column} : {pearson}')

#compute covariance matrix
cov_matrix = df.cov()
print("\nCovariance matrix:\n", cov_matrix)

#compute correlation matrix
corr_matrix = df.corr()
print("\n\n\nCorrelation matrix:\n", corr_matrix)

#visualize correlation matrix using heatmap
plt.figure(figsize=(10,8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths = 0.5)
plt.title('Correlation Matrix Heatmap')
plt.show()
""",
"""#LAB3
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load the Iris dataset
iris = datasets.load_iris()
X = iris.data
y = iris.target

# Standardize the features
scaler = StandardScaler()
X_standardized = scaler.fit_transform(X)

# Apply PCA
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X_standardized)

# Create a DataFrame for plotting
df = pd.DataFrame(X_reduced, columns=['PCA1', 'PCA2'])
df['target'] = y

# Plotting the PCA results
plt.figure(figsize=(10, 7))
colors = ['r', 'g', 'b']
for target, color in zip(np.unique(y), colors):
    subset = df[df['target'] == target]
    plt.scatter(subset['PCA1'], subset['PCA2'], color=color, label=iris.target_names[target])
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA of Iris Dataset (Using Scikit-learn)')
plt.legend()
plt.show()""",
"""#LAB4
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsClassifier

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Standardize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Evaluate for different k values (unweighted)
k_values = [1, 3, 5]
for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k, weights='uniform')  # Regular k-NN
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f'k={k}, Regular k-NN -> Accuracy: {acc:.4f}, F1-score: {f1:.4f}')

# Evaluate for different k values (weighted)
for k in k_values:
    knn_weighted = KNeighborsClassifier(n_neighbors=k, weights='distance')  # Weighted k-NN
    knn_weighted.fit(X_train, y_train)
    y_pred_weighted = knn_weighted.predict(X_test)
    acc_weighted = accuracy_score(y_test, y_pred_weighted)
    f1_weighted = f1_score(y_test, y_pred_weighted, average='weighted')
    print(f'k={k}, Weighted k-NN -> Accuracy: {acc_weighted:.4f}, F1-score: {f1_weighted:.4f}')
""",
"""#LAB5

import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import inv

#GENERATE SYNTHETIC DATASET
np.set_printoptions(linewidth=np.inf)
np.random.seed(0)
X=np.linspace(-3,3,100)
y=np.sin(X)+np.random.normal(0,0.1,X.shape)
plt.scatter(X,y,alpha=0.8)
plt.show()
#ADD INTERCEPT TERM FOR BIAS
X_bias = np.c_[np.ones(X.shape[0]),X]

def weighted_linear_regression(X, y, tau, x_query):
    #Perform locally weighted regression for a single query point.
    m = X.shape[0]
    W = np.eye(m)  # Weight matrix
    for i in range(m):
        W[i, i] = np.exp(-np.sum((X[i] - x_query)**2) / (2 * tau**2))  # Gaussian kernel
    # Ensure X.T @ W @ X is invertible
    theta = inv(X.T @ W @ X) @ (X.T @ W @ y)
    return x_query @ theta

# Locally Weighted Regression
def locally_weighted_regression(X, y, tau, X_test):
    #Apply LWR to a set of test points.
    y_pred = np.array([weighted_linear_regression(X, y, tau, x_query) for x_query in X_test])
    return y_pred

#TEST POINTS FOR PREDICTION
X_test = np.linspace(-3, 3, 25)
X_test_bias = np.c_[np.ones(X_test.shape[0]), X_test]

# Evaluate and visualize Locally Weighted Regression for different tau values
tau_values = [0.01, 0.3, 1, 3]
for tau in tau_values:
    y_pred = locally_weighted_regression(X_bias, y, tau, X_test_bias)
    plt.scatter(X, y, label="Data", color="blue", alpha=0.6)
    plt.plot(X_test, y_pred, label=f"LWR Fit (tau={tau})", color='red')
    plt.xlabel("X")
    plt.ylabel("y")
    plt.legend()
    plt.title(f"Locally Weighted Regression (tau={tau})")
    plt.show()""",
"""#LAB 6a
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
X = housing.data[:700]
y = housing.target[:700]

# Convert to DataFrame for better readability
housing_df = pd.DataFrame(X, columns=housing.feature_names)
print(f"number of attributes = {len(housing_df.columns)}")
housing_df['Price'] = y

# Split the data into training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a linear regression model
model = LinearRegression()

# Train the model using the training data

model.fit(X_train, y_train)
print("Intercept - beta value:", model.intercept_)
print("Coefficients - beta value:", model.coef_)

# Predict on the test data
y_pred = model.predict(X_test)

# Plotting the true vs predicted values
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--')
plt.title("True vs Predicted Prices")
plt.xlabel("True Prices")
plt.ylabel("Predicted Prices")
plt.show()

# Calculate performance metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
# Print the results
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")
print(f"R2 Score: {r2}")


#LAB 6b

from sklearn.metrics import mean_squared_error, r2_score

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Read dataset
df = pd.read_csv("auto-mpg.csv")
print("before data preprocessing - Number of rows:", df.shape[0])

# Convert "?" to NaN and drop missing values
df.replace("?", np.nan, inplace=True)
df.dropna(inplace=True)
print("after data preprocessing - Number of rows:", df.shape[0])

# Convert 'horsepower' column to numeric
df["horsepower"] = df["horsepower"].astype(float)

# Selecting Features and Target
X = df[["displacement", "horsepower", "weight", "acceleration"]]
y = df["mpg"]

# Splitting Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Apply Polynomial Transformation (Degree = 2)
poly = PolynomialFeatures(degree=2)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Standardize the Data (Polynomial Features Can Grow Large)
scaler = StandardScaler()
X_train_poly = scaler.fit_transform(X_train_poly)
X_test_poly = scaler.transform(X_test_poly)

# Train the Linear Regression Model
model = LinearRegression()
model.fit(X_train_poly, y_train)

# Predict MPG Values
y_pred = model.predict(X_test_poly)

# Evaluate the Model using mse,rmse,r2 Score
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")
print("Polynomial Regression R2 Score:", r2)

# Scatter Plot: Actual vs. Predicted MPG
plt.scatter(y_test, y_pred, color='blue', label="Predicted vs Actual")
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label="Perfect Fit")
plt.xlabel("Actual MPG")
plt.ylabel("Predicted MPG")

plt.legend()
plt.title("Polynomial Regression: Actual vs Predicted MPG")
plt.show()""",
"""#LAB 7

# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

# Load Titanic dataset from seaborn
df = sns.load_dataset('titanic')

# Drop rows with missing target or key features
df = df.dropna(subset=['age', 'embarked', 'sex', 'fare', 'pclass', 'survived'])

# Encode categorical variables
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df['embarked'] = df['embarked'].map({'S': 0, 'C': 1, 'Q': 2})
# Select features and target
features = ['pclass', 'sex', 'age', 'fare', 'embarked']
X = df[features]
y = df['survived']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=42)

# Train a Decision Tree Classifier
clf = DecisionTreeClassifier(
criterion='entropy',
max_depth=3,
min_samples_split=5,
min_samples_leaf=5,
random_state=42
)
#clf = DecisionTreeClassifier(max_depth=3,random_state=42)
clf.fit(X_train, y_train)

# Visualize the decision tree
plt.figure(figsize=(30,40))
plot_tree(clf, feature_names=features, class_names=["Not Survived","Survived"], filled=True)
plt.title("Decision Tree using CART - gini/entropy index - Titanic")
plt.show()

# Predict on the test set
y_pred = clf.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

# Print evaluation metrics
print("Model Evaluation Metrics:")
print(f"Accuracy : {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall : {recall:.2f}")
print(f"F1-Score : {f1:.2f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))""",
"""#LAB 8

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Step 1: Load the dataset
iris = load_iris()
X = iris.data # Features
y = iris.target # Labels

# Step 2: Split the dataset into training and test data (60% train, 40% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

# Step 3: Initialize and train the Naive Bayes classifier
model = GaussianNB()
model.fit(X_train, y_train)

# Step 4: Make predictions
y_pred = model.predict(X_test)

# Step 5: Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)

# Display results
print("Naive Bayes Classifier Accuracy: {:.2f}%".format(accuracy * 100))
print("\nClassification Report:\n", classification_report(y_test, y_pred,target_names=iris.target_names))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))""",
"""#LAB 9

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load dataset from sklearn
data = load_breast_cancer()

# Get features and labels
X = data.data
y = data.target

# Show the shape of the data (569 samples, 30 features)
print("Data Shape:", X.shape)
print("Target Shape:", y.shape)

# ====== Standardize the Data ======Standardize the data (important for k-means)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ====== Apply K-Means Clustering ======
kmeans = KMeans(n_clusters=3, random_state=42) # 2 clusters for malignant and benign
kmeans.fit(X_scaled)

# Get cluster labels
y_kmeans = kmeans.labels_

# Let's plot using the first two features to create a 2D plot
plt.figure(figsize=(8, 6))

# Plot points colored by cluster label
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y_kmeans, cmap='viridis', marker='o')

# Plot the cluster centers
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='blue', marker='x', s=100, label='Centroids')
plt.title('K-Means Clustering on Breast Cancer Dataset')
plt.xlabel('Feature 1 (scaled)')
plt.ylabel('Feature 2 (scaled)')
plt.legend()
plt.show()

# If we want to compare with the actual labels (malignant: 0, benign: 1)
# Since we know that we have 2 clusters (malignant, benign), let's compare the clusters with the true labels
print("Confusion Matrix:\n", confusion_matrix(y, y_kmeans))
print("\nClassification Report:\n", classification_report(y, y_kmeans))"""
    ]
    print(mlprogs[indx+1])

def print_genai_programs(indx):
    genaiprogs=["""Program 1 (original) :
import gensim.downloader as api
# Load pre-trained model
model = api.load("glove-wiki-gigaword-50")
# Example words
word1 = "king"
word2 = "man"
word3 = "woman"
# Performing vector arithmetic
result_vector = model[word1] - model[word2] + model[word3]
predicted_word = model.most_similar([result_vector], topn=2)
print(f"Result of '{word1} - {word2} + {word3}' is: {predicted_word[1][0]}”)
           
Program 1 (oﬄine compatible) :
from gensim.models import KeyedVectors
# Load pre-downloaded GloVe model
model_path = "glove-wiki-gigaword-50.kv" # Preconverted and saved as KeyedVectors format
model = KeyedVectors.load(model_path)
# Example words
word1 = "king"
word2 = "man"
word3 = "woman"
# Performing vector arithmetic
result_vector = model[word1] - model[word2] + model[word3]
predicted_word = model.most_similar([result_vector], topn=2)
print(f"Result of '{word1} - {word2} + {word3}' is: {predicted_word[1][0]}”)""",
"""Program 2 (original) :

import gensim.downloader as api
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
# Load pre-trained Word2Vec model
model = api.load("glove-wiki-gigaword-50")
# Select 10 words from a specific domain (e.g., technology)
words = ["computer", "internet", "software", "hardware", "disk", "robot", "data",
"network", "cloud", "algorithm"]
# Get word vectors and convert to a 2D NumPy array
word_vectors = np.array([model[word] for word in words])
# Reduce dimensions using PCA
pca = PCA(n_components=2)
reduced_vectors = pca.fit_transform(word_vectors)
# Plot PCA visualization
plt.figure(figsize=(8, 6))
for i, word in enumerate(words):
plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1])
plt.annotate(word, (reduced_vectors[i, 0], reduced_vectors[i, 1]))
plt.title("PCA Visualization of Word Embeddings (Technology Domain)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.show()
input_word = "computer" # You can change this to any word in your list
similar_words = model.most_similar(input_word, topn=5)
print(f"Words similar to '{input_word}':", similar_words)


Program 2 (offline compatible) :

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
import gensim
from gensim.models import KeyedVectors

# Load the pre-downloaded GloVe vectors in word2vec format
model = KeyedVectors.load("glove-wiki-gigaword-50.kv")

# Select 10 words from a specific domain (e.g., technology)
words = ["computer", "internet", "software", "hardware", "disk", "robot", "data",
         "network", "cloud", "algorithm"]

# Get word vectors and convert to a 2D NumPy array
word_vectors = np.array([model[word] for word in words])

# Reduce dimensions using PCA
pca = PCA(n_components=2)
reduced_vectors = pca.fit_transform(word_vectors)

# Plot PCA visualization
plt.figure(figsize=(8, 6))
for i, word in enumerate(words):
    plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1])
    plt.annotate(word, (reduced_vectors[i, 0], reduced_vectors[i, 1]))
plt.title("PCA Visualization of Word Embeddings (Technology Domain)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.show()

# Find similar words
input_word = "computer"  # You can change this to any word in your list
similar_words = model.most_similar(input_word, topn=5)
print(f"Words similar to '{input_word}':", similar_words)""",
"""Program 3 (original) :

import gensim
from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize

# Sample domain-specific dataset (Medical domain)
corpus = [
    "A patient with diabetes requires regular insulin injections.",
    "Medical professionals recommend exercise for heart health.",
    "Doctors use MRI scans to diagnose brain disorders.",
    "Antibiotics help fight bacterial infections but not viral infections.",
    "The surgeon performed a complex cardiac surgery successfully.",
    "Doctors and nurses work together to treat patients.",
    "A doctor specializes in diagnosing and treating diseases."
]

# Tokenize sentences
tokenized_corpus = [word_tokenize(sentence.lower()) for sentence in corpus]

# Train Word2Vec model (Using Skip-gram)
model = Word2Vec(
    sentences=tokenized_corpus,
    vector_size=100,
    window=3,
    min_count=1,
    workers=4,
    sg=1
)

# Save the model
model.save("medical_word2vec.model")

# Test trained model - Find similar words
similar_words = model.wv.most_similar("doctor", topn=5)

# Display results
print("Top 5 words similar to 'doctor':")
print(similar_words)


Program 3 (offline compatible):

No changes needed""",
"""Program 4 (original) :

from transformers import pipeline
import gensim.downloader as api

# Load pre-trained GloVe embeddings
glove_model = api.load("glove-wiki-gigaword-50")

word = "technology"
similar_words = glove_model.most_similar(word, topn=5)
print(f"Similar words to '{word}': {similar_words}")

# Load a text generation pipeline
generator = pipeline("text-generation", model="gpt2")

# Function to generate text
def generate_response(prompt, max_length=100):
    response = generator(prompt, max_length=max_length, num_return_sequences=1)
    return response[0]['generated_text']

# Original prompt
original_prompt = "Explain the impact of technology on society."
original_response = generate_response(original_prompt)

# Enriched prompt
enriched_prompt = "Explain the impact of technology, innovation, science, engineering, and digital advancements on society."
enriched_response = generate_response(enriched_prompt)

# Print responses
print("Original Prompt Response:")
print(original_response)

print("\nEnriched Prompt Response:")
print(enriched_response)


Program 4 (offline compatible) :

from gensim.models import KeyedVectors
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Load local GloVe embeddings (converted beforehand)
glove_model = KeyedVectors.load("glove.kv")

word = "technology"
similar_words = glove_model.most_similar(word, topn=5)
print(f"Similar words to '{word}': {similar_words}")

# Load GPT-2 model and tokenizer from local directory
tokenizer = AutoTokenizer.from_pretrained("./gpt2-local")
model = AutoModelForCausalLM.from_pretrained("./gpt2-local")

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def generate_response(prompt, max_length=100):
    response = generator(prompt, max_length=max_length, num_return_sequences=1)
    return response[0]['generated_text']

original_prompt = "Explain the impact of technology on society."
original_response = generate_response(original_prompt)

enriched_prompt = "Explain the impact of technology, innovation, science, engineering, and digital advancements on society."
enriched_response = generate_response(enriched_prompt)

print("Original Prompt Response:")
print(original_response)

print("\nEnriched Prompt Response:")
print(enriched_response)""",
"""Program 5 (original) :

import gensim.downloader as api

# Load GloVe embeddings directly
model = api.load("glove-wiki-gigaword-50")

# Function to construct a short paragraph
def construct_paragraph(seed_word, similar_words):
    # Create a simple template-based paragraph
    paragraph = (
        f"In the spirit of {seed_word}, one might embark on an unforgettable {similar_words[0][0]} "
        f"to distant lands. Every {similar_words[1][0]} brings new challenges and opportunities for {similar_words[2][0]}. "
        f"Through perseverance and courage, the {similar_words[3][0]} becomes a tale of triumph, much like an {similar_words[4][0]}."
    )
    return paragraph

# Generate a paragraph for "adventure"
seed_word = "adventure"
similar_words = model.most_similar(seed_word, topn=5)

# Construct a paragraph
paragraph = construct_paragraph(seed_word, similar_words)
print(paragraph)

Program 5 (offline compatible) :

from gensim.models import KeyedVectors

# Load local GloVe embeddings
model = KeyedVectors.load("glove.kv")

def construct_paragraph(seed_word, similar_words):
    paragraph = (
        f"In the spirit of {seed_word}, one might embark on an unforgettable {similar_words[0][0]} "
        f"to distant lands. Every {similar_words[1][0]} brings new challenges and opportunities for {similar_words[2][0]}. "
        f"Through perseverance and courage, the {similar_words[3][0]} becomes a tale of triumph, much like an {similar_words[4][0]}."
    )
    return paragraph

seed_word = "adventure"
similar_words = model.most_similar(seed_word, topn=5)

paragraph = construct_paragraph(seed_word, similar_words)
print(paragraph)""",
"""Program 6 (original) :

from transformers import pipeline

# Load the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Example sentences
sentences = [
    "I love this product! It works perfectly.",
    "This is the worst experience I've ever had.",
    "The weather is nice today.",
    "I feel so frustrated with this service."
]

# Analyze sentiment for each sentence
results = sentiment_pipeline(sentences)

# Print the results
for sentence, result in zip(sentences, results):
    print(f"Sentence: {sentence}")
    print(f"Sentiment: {result['label']}, Confidence: {result['score']:.4f}")
    print()

Program 6 (offline compatible) :
Assumes you’ve saved a pre-trained model (e.g., distilbert-base-uncased-finetuned-sst-2-english) locally in ./sentiment-local/


from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Load local model for sentiment analysis
model = AutoModelForSequenceClassification.from_pretrained("./sentiment-local")
tokenizer = AutoTokenizer.from_pretrained("./sentiment-local")
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

sentences = [
    "I love this product! It works perfectly.",
    "This is the worst experience I've ever had.",
    "The weather is nice today.",
    "I feel so frustrated with this service."
]

results = sentiment_pipeline(sentences)

for sentence, result in zip(sentences, results):
    print(f"Sentence: {sentence}")
    print(f"Sentiment: {result['label']}, Confidence: {result['score']:.4f}")
    print()""",
"""Program 7 (original) :
from transformers import pipeline

# Load the T5 summarization pipeline
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Example passage
passage = (
    "Machine learning is a subset of artificial intelligence that focuses on training algorithms "
    "to make predictions. It is widely used in industries like healthcare, finance, and retail."
)

# Generate the summary
summary = summarizer(passage, max_length=30, min_length=10, do_sample=False)

# Print the summarized text
print("Summary:")
print(summary[0][‘summary_text'])


Program 7 (offline compatible) :
Assumes you’ve downloaded and saved the T5 model to ./t5-small-local/


from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Load the T5 summarization model locally
model = AutoModelForSeq2SeqLM.from_pretrained("./t5-small-local")
tokenizer = AutoTokenizer.from_pretrained("./t5-small-local")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

passage = (
    "Machine learning is a subset of artificial intelligence that focuses on training algorithms "
    "to make predictions. It is widely used in industries like healthcare, finance, and retail."
)

summary = summarizer(passage, max_length=30, min_length=10, do_sample=False)

print("Summary:")
print(summary[0]['summary_text'])""",
"""Program 8 (original) :

import os
from cohere import Client
from langchain.prompts import PromptTemplate

# Step 1: Set Cohere API Key
os.environ["COHERE_API_KEY"] = "RI01YSU6DETF3yEF0MTwwbOOjIsVWRedqTpN627v"
co = Client(os.getenv("COHERE_API_KEY"))

# Step 2: Load Text Document (Local File)
with open("C:/Users/nagab/Documents/BIT/GenAI/APIKey.txt", "r", encoding="utf-8") as file:
    text_document = file.read()

# Step 3: Create a Prompt Template
template = '''
You are an expert summarizer. Summarize the following text in a concise manner:
Text: {text}
Summary:
'''
prompt_template = PromptTemplate(input_variables=["text"], template=template)
formatted_prompt = prompt_template.format(text=text_document)

# Step 4: Send Prompt to Cohere API
response = co.generate(
    model="command",
    prompt=formatted_prompt,
    max_tokens=50
)

# Step 5: Display Output
print("Summary:")
print(response.generations[0].text.strip())


Program 8 (offline compatible) :
Use a local HuggingFace summarization model instead of Cohere

from transformers import pipeline

# Load local summarization model (e.g., t5-small in ./t5-small-local/)
summarizer = pipeline("summarization", model="./t5-small-local", tokenizer="./t5-small-local")

# Load the text document
with open("C:/Users/nagab/Documents/BIT/GenAI/APIKey.txt", "r", encoding="utf-8") as file:
    text_document = file.read()

# Summarize the document
summary = summarizer(text_document, max_length=50, min_length=10, do_sample=False)

# Display the summary
print("Summary:")
print(summary[0]['summary_text'])""",
"""Program 9 (original) :

from typing import Optional
from pydantic import BaseModel, Field, ValidationError
import wikipedia

# Step 1: Define the Pydantic Schema
class InstitutionDetails(BaseModel):
    name: str = Field(description="Name of the institution")
    founder: Optional[str] = Field(description="Founder of the institution")
    founding_year: Optional[int] = Field(description="Year the institution was founded")
    branches: Optional[int] = Field(description="Number of branches")
    employees: Optional[int] = Field(description="Number of employees")
    summary: Optional[str] = Field(description="Summary of the institution")

# Step 2: Fetch Institution Details from Wikipedia
def fetch_institution_details(institution_name: str) -> InstitutionDetails:
    try:
        page = wikipedia.page(institution_name)
        summary = wikipedia.summary(institution_name, sentences=3)

        details = {
            "name": institution_name,
            "founder": None,  # NLP/regex-based parsing can be added
            "founding_year": None,
            "branches": None,
            "employees": None,
            "summary": summary,
        }
        return InstitutionDetails(**details)

    except wikipedia.exceptions.PageError:
        return InstitutionDetails(name=institution_name, summary="No Wikipedia page found.")
    except wikipedia.exceptions.DisambiguationError:
        return InstitutionDetails(name=institution_name, summary="Multiple matches found. Please specify.")
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return InstitutionDetails(name=institution_name, summary="Error parsing details.")

# Step 3: Run the Program
if __name__ == "__main__":
    institution_name = input("Enter the institution name: ")
    details = fetch_institution_details(institution_name)
    print(details)


Program 9 (offline compatible) :
If full Wikipedia API access is unavailable, simulate with a local text file or cached content

from typing import Optional
from pydantic import BaseModel, Field, ValidationError

# Simulated offline database (JSON-like dictionary or file)
offline_data = {
    "IIT Madras": {
        "founder": "Indian Government",
        "founding_year": 1959,
        "branches": 1,
        "employees": 1000,
        "summary": "IIT Madras is a premier engineering institution located in Chennai, India."
    },
    "MIT": {
        "founder": "William Barton Rogers",
        "founding_year": 1861,
        "branches": 1,
        "employees": 12000,
        "summary": "MIT is a world-renowned institute located in Cambridge, Massachusetts."
    }
}

class InstitutionDetails(BaseModel):
    name: str = Field(description="Name of the institution")
    founder: Optional[str]
    founding_year: Optional[int]
    branches: Optional[int]
    employees: Optional[int]
    summary: Optional[str]

def fetch_institution_details(institution_name: str) -> InstitutionDetails:
    data = offline_data.get(institution_name)
    if data:
        return InstitutionDetails(name=institution_name, **data)
    else:
        return InstitutionDetails(name=institution_name, summary="Institution data not available offline.")

if __name__ == "__main__":
    institution_name = input("Enter the institution name: ")
    details = fetch_institution_details(institution_name)
    print(details)""",
"""Program 10 (original) :

import pdfplumber
import ollama

# Load and extract text from PDF
with pdfplumber.open("R&D_visit_report.pdf") as pdf:
    full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

# Chat loop
print("IPC Chatbot Ready. Ask anything about the Indian Penal Code.")
while True:
    query = input("\nYou: ")
    if query.lower() in ["exit", "quit"]:
        print("Chatbot: Goodbye!")
        break

    prompt = f'''You are a helpful assistant.
{full_text[:6000]}  # limit text to avoid going over context length

Question: {query}
Answer:'''

    response = ollama.chat(model="deepseek-r1:1.5b", messages=[{"role": "user", "content": prompt}])
    print(f"Chatbot: {response[‘message']['content']}")


Program 10 (offline compatible) :

No changes"""]
    print(genaiprogs[indx+1])