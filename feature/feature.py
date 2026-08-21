import json
import numpy

vectors = []
labels = []

with open("../data/collected_matches/matches.json", "r") as f: 
	for line in f:
		match = json.loads(line)
		v = [0] * 127

		for hero_id in match["radiant_draft"]:
			v[hero_id] = 1

		for hero_id in match["dire_draft"]:
			v[hero_id] = -1


		v.append(1)
		vectors.append(v)
		labels.append(1 if match["radiant_win"] else 0)


X = numpy.array(vectors)
Y = numpy.array(labels)

print(Y)

numpy.save("../data/collected_matches/X.npy", X)
numpy.save("../data/collected_matches/Y.npy", Y)
print(f"Saved X{X.shape} Y{Y.shape}")