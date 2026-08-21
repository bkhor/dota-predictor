import json
import numpy
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/collected_matches")


def run():
	vectors = []
	labels = []

	with open(os.path.join(DATA_DIR, "matches.json"), "r") as f:
		for line in f:
			match = json.loads(line)
			v = [0] * 156

			for hero_id in match["radiant_draft"]:
				v[hero_id] = 1

			for hero_id in match["dire_draft"]:
				v[hero_id] = -1

			v.append(1)
			vectors.append(v)
			labels.append(1 if match["radiant_win"] else 0)

	X = numpy.array(vectors)
	Y = numpy.array(labels)

	numpy.save(os.path.join(DATA_DIR, "X.npy"), X)
	numpy.save(os.path.join(DATA_DIR, "Y.npy"), Y)
	print(f"Saved X{X.shape} Y{Y.shape}")
	
if __name__ == "__main__":
    run()