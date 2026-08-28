import json
import os

import numpy

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
WEIGHTS_PATH = os.path.join(DATA_DIR, "weights.npy")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "../metrics.json")

learning_rate = 0.01
hard_prediction_threshold = 0.5
epochs = 1000


def sigmoid(z):
    return 1 / (1 + numpy.exp(-z))


def prediction(X, weights):
    return sigmoid(numpy.dot(X, weights))


def binary_cross_entropy(Y, Y_predicted, epsilon=1e-15):
    Y_predicted = numpy.clip(Y_predicted, epsilon, 1 - epsilon)
    n = len(Y)
    return -numpy.sum(Y * numpy.log(Y_predicted) + (1 - Y) * numpy.log(1 - Y_predicted)) / n


def compute_gradient(X, Y, Y_predicted):
    return X.T @ (Y_predicted - Y) / X.shape[0]


def update_weights(weights, gradient, learning_rate):
    return weights - learning_rate * gradient


def to_hard_predictions(Y_predicted):
    return (Y_predicted >= hard_prediction_threshold).astype(int)


def train(X, Y, weights, learning_rate, epochs, batch_size=128):
    n = len(X)
    for epoch in range(epochs):
        indices = numpy.random.permutation(n)
        X_shuffled = X[indices]
        Y_shuffled = Y[indices]

        for i in range(0, n, batch_size):
            X_batch = X_shuffled[i:i + batch_size]
            Y_batch = Y_shuffled[i:i + batch_size]

            Y_hat = prediction(X_batch, weights)
            gradient = compute_gradient(X_batch, Y_batch, Y_hat)
            weights = update_weights(weights, gradient, learning_rate)

        if epoch % 100 == 0:
            loss = binary_cross_entropy(Y, prediction(X, weights))
            print(f"Epoch {epoch} loss: {loss:.4f}")

    return weights


def run():
    X = numpy.load(os.path.join(DATA_DIR, "X.npy"))
    Y = numpy.load(os.path.join(DATA_DIR, "Y.npy"))

    if os.path.exists(WEIGHTS_PATH):
        weights = numpy.load(WEIGHTS_PATH)
        print("Loaded existing weights")
    else:
        weights = numpy.zeros(X.shape[1])

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    Y_train, Y_test = Y[:split], Y[split:]

    trained_weights = train(X_train, Y_train, weights, learning_rate, epochs)

    numpy.save(WEIGHTS_PATH, trained_weights)
    print("Saved weights")

    Y_hat = prediction(X_test, trained_weights)
    accuracy = float(numpy.mean(to_hard_predictions(Y_hat) == Y_test))
    print(f"Test accuracy: {accuracy:.4f}")

    with open(METRICS_PATH, "w") as f:
        json.dump({"accuracy": round(accuracy, 4)}, f)
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    run()
