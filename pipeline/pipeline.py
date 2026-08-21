import sys
sys.path.append("../data")
sys.path.append("../feature")
sys.path.append("../model")

import collection
import feature
import train

if __name__ == "__main__":
    print("=== Collecting ===")
    collection.run()

    print("=== Featurizing ===")
    feature.run()

    print("=== Training ===")
    train.run()