import json
import os
import sys

import numpy

sys.path.append(os.path.join(os.path.dirname(__file__), "../data"))
from db import get_all_matches

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")


def build_vector(radiant_draft, dire_draft):
    v = [0] * 156
    for hero_id in radiant_draft:
        v[hero_id] = 1
    for hero_id in dire_draft:
        v[hero_id] = -1
    v.append(1)  # bias
    return v


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    matches = get_all_matches()

    vectors = []
    labels = []

    for match in matches:
        radiant_draft = json.loads(match["radiant_draft"])
        dire_draft = json.loads(match["dire_draft"])

        vectors.append(build_vector(radiant_draft, dire_draft))
        labels.append(1 if match["radiant_win"] else 0)

        # augment: flip radiant/dire, flip label
        vectors.append(build_vector(dire_draft, radiant_draft))
        labels.append(0 if match["radiant_win"] else 1)

    X = numpy.array(vectors)
    Y = numpy.array(labels)

    numpy.save(os.path.join(OUTPUT_DIR, "X.npy"), X)
    numpy.save(os.path.join(OUTPUT_DIR, "Y.npy"), Y)
    print(f"Saved X{X.shape} Y{Y.shape}")


if __name__ == "__main__":
    run()
