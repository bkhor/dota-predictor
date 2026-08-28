import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../feature"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../model"))

import collection
import feature
import logistic_regression
import patches
import winrates

if __name__ == "__main__":
    print("=== Collecting ===")
    collection.run()

    print("=== Assigning Patches ===")
    patches.run()

    print("=== Computing Winrates ===")
    winrates.run()

    print("=== Featurizing ===")
    feature.run()

    print("=== Training ===")
    logistic_regression.run()
