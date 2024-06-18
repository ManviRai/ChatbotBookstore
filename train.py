import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import json
import random
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

# Load dataset
with open("intents.json") as file:
    data = json.load(file)

# Extract intents and patterns
intents = data["intents"]

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Initialize lists
words = []
classes = []
documents = []
ignore_words = ["?", "!"]

# Process intents and patterns
for intent in intents:
    for pattern in intent["patterns"]:
        # Tokenize the pattern
        w = nltk.word_tokenize(pattern)
        # Extend words list
        words.extend(w)
        # Add documents
        documents.append((w, intent["tag"]))
        # Add classes to classes list
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

# Filter out ignore_words and sort words
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Filter out classes with 'EMPTY_PATTERN'
classes = sorted(list(set(classes)))
classes = [c for c in classes if c != 'EMPTY_PATTERN']

# Print information about the data
print(len(documents), "documents")
print(len(classes), "classes", classes)
print(len(words), "unique lemmatized words", words)

# Initialize training data
training = []
output_empty = [0] * len(classes)

# Build training data
for doc in documents:
    # Initialize bag of words
    bag = []
    # List of tokenized words for the pattern
    pattern_words = doc[0]
    # Lemmatize each word
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # Create bag of words array with 1 if word match found in current pattern
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # Output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    # Append bag of words and output to training data
    training.append([bag, output_row])

# Shuffle training data
random.shuffle(training)

# Separate features and labels
train_x = np.array([x[0] for x in training])
train_y = np.array([x[1] for x in training])

print("Training data created")

# Create model
model = Sequential([
    Dense(128, input_shape=(len(train_x[0]),), activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(len(train_y[0]), activation='softmax')
])

# Compile model
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train model
history = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

print("Model trained")

# Save words and classes using pickle
pickle.dump(words, open("words.pkl", "wb"))
pickle.dump(classes, open("classes.pkl", "wb"))

# Save model
model.save("chatbot_model.h5")

print("Model, words, and classes saved to disk")
