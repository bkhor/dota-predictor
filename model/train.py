import numpy 

weights = numpy.zeros(128)
X = numpy.load("../data/collected_matches/X.npy")
Y = numpy.load("../data/collected_matches/Y.npy")

learning_rate = 0.1
hard_prediction_threshold = 0.5
epochs = 1000


def sigmoid(z):
	return 1 / (1 + numpy.exp(-z))


def prediction(X, weights):
	return sigmoid(numpy.dot(X, weights))

def binary_cross_entropy(Y, Y_predicted, epsilon=1e-15):
	Y_predicted = numpy.clip(Y_predicted, epsilon, 1 - epsilon)
	n = len(Y)
	loss = -numpy.sum(Y * numpy.log(Y_predicted) + (1 - Y) * numpy.log(1 - Y_predicted)) / n
	return loss

def compute_gradient(X, Y, Y_predicted):
	n = X.shape[0]
	gradient = X.T @ (Y_predicted - Y) / n
	return gradient

def update_weights(weights, gradient, learning_rate):
	weights = weights - learning_rate * gradient
	return weights

def to_hard_predictions(Y_predicted):
	return (Y_predicted >= hard_prediction_threshold).astype(int)

def train(X, Y, weights, learning_rate, epochs):
	for epoch in range(epochs):
		Y_hat = prediction(X, weights)
		loss = binary_cross_entropy(Y, Y_hat)
		gradient = compute_gradient(X, Y, Y_hat)
		weights = update_weights(weights, gradient, learning_rate)
		if epoch % 10 == 0:
			print(f"Epoch {epoch} loss: {loss:.4f}")
	return weights

if __name__ == "__main__":
	split = int(0.8 * len(X))
	X_train, X_test = X[:split], X[split:]
	Y_train, Y_test = Y[:split], Y[split:]

	trained_weights = train(X_train, Y_train, weights, learning_rate, epochs)

	Y_hat = prediction(X_test, trained_weights)
	hard = to_hard_predictions(Y_hat)
	accuracy = numpy.mean(hard == Y_test)
	print(f"Test accuracy: {accuracy:.4f}")

