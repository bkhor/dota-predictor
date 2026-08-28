import json
import os
import sys

import numpy

sys.path.append(os.path.join(os.path.dirname(__file__), "../data"))
from db import get_all_matches, get_hero_stats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")


def load_winrates():
    winrates = {}
    for hero_id in range(156):
        stat = get_hero_stats(hero_id, patch=0)
        if stat:
            winrates[hero_id] = (stat["winrate"] - 0.5) * 2  # normalize to [-1, 1]
    return winrates


def build_vector(radiant_draft, dire_draft, winrates):
    v = [0] * 156
    for hero_id in radiant_draft:
        v[hero_id] = 1
    for hero_id in dire_draft:
        v[hero_id] = -1
    v.append(1)  # bias

    # append winrates for each pick: 5 radiant + 5 dire
    for hero_id in radiant_draft:
        v.append(winrates.get(hero_id, 0.0))
    for hero_id in dire_draft:
        v.append(winrates.get(hero_id, 0.0))

    return v


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    matches = get_all_matches()
    winrates = load_winrates()
    print(f"Loaded winrates for {len(winrates)} heroes")

    vectors = []
    labels = []

    for match in matches:
        radiant_draft = json.loads(match["radiant_draft"])
        dire_draft = json.loads(match["dire_draft"])

        vectors.append(build_vector(radiant_draft, dire_draft, winrates))
        labels.append(1 if match["radiant_win"] else 0)

        # augment: flip radiant/dire, flip label
        vectors.append(build_vector(dire_draft, radiant_draft, winrates))
        labels.append(0 if match["radiant_win"] else 1)

    X = numpy.array(vectors)
    Y = numpy.array(labels)

    numpy.save(os.path.join(OUTPUT_DIR, "X.npy"), X)
    numpy.save(os.path.join(OUTPUT_DIR, "Y.npy"), Y)
    print(f"Saved X{X.shape} Y{Y.shape}")


if __name__ == "__main__":
    run()
