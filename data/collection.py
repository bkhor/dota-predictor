import requests
from dataclasses import dataclass
import json
import os
import time

BASE_OPENDOTA_EXPLORER_API_URL = "https://api.opendota.com/api/explorer"
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "collected_matches")
SEEN_IDS_PATH = os.path.join(OUTPUT_FOLDER, "seen_ids.txt")
LAST_ID_PATH = os.path.join(OUTPUT_FOLDER, "last_match_id.txt")


@dataclass
class Match:
	radiant_win: bool
	radiant_draft: list
	dire_draft: list


def fetch_batch(less_than_match_id):
	sql = f"""
        SELECT match_id, radiant_win, picks_bans
        FROM matches
        WHERE picks_bans IS NOT NULL
        AND match_id < {less_than_match_id}
        ORDER BY match_id DESC
        LIMIT 1000
    """
	response = requests.get(BASE_OPENDOTA_EXPLORER_API_URL, params={"sql": sql})
	response.raise_for_status()
	data = response.json()
	return data["rows"]


def parse_match(row):
	picks = [p for p in row["picks_bans"] if p["is_pick"]]
	radiant_picks = [p["hero_id"] for p in picks if p["team"] == 0]
	dire_picks = [p["hero_id"] for p in picks if p["team"] == 1]

	if len(radiant_picks) != 5 or len(dire_picks) != 5:
		return None

	return Match(
		radiant_win=row["radiant_win"],
		radiant_draft=radiant_picks,
		dire_draft=dire_picks
	)


def parse_batch(rows):
	matches = []
	for row in rows:
		match = parse_match(row)
		if match is not None:
			matches.append(match)
	return matches


def to_json(matches):
	path = f"{OUTPUT_FOLDER}/matches.json"
	with open(path, "a") as f:
		for match in matches:
			f.write(json.dumps({
				"radiant_win": match.radiant_win,
				"radiant_draft": match.radiant_draft,
				"dire_draft": match.dire_draft
			}) + "\n")


def load_seen_ids():
	if not os.path.exists(SEEN_IDS_PATH):
		return set()
	with open(SEEN_IDS_PATH) as f:
		return set(int(line.strip()) for line in f)


def save_seen_ids(ids):
	with open(SEEN_IDS_PATH, "a") as f:
		for id in ids:
			f.write(str(id) + "\n")


def load_last_match_id():
	if not os.path.exists(LAST_ID_PATH):
		return 999999999999
	with open(LAST_ID_PATH) as f:
		return int(f.read().strip())


def save_last_match_id(match_id):
	with open(LAST_ID_PATH, "w") as f:
		f.write(str(match_id))


MIN_MATCH_ID = 6000000000  # matches from ~2021 onwards

def run(target=1000000):
	seen_ids = load_seen_ids()
	less_than_match_id = load_last_match_id()
	total = 0

	while total < target:
		if less_than_match_id < MIN_MATCH_ID:
			print("Reached minimum match ID limit")
			break
		rows = fetch_batch(less_than_match_id)
		if not rows:
			break

		new_rows = [r for r in rows if r["match_id"] not in seen_ids]
		matches = parse_batch(new_rows)
		to_json(matches)

		new_ids = [r["match_id"] for r in new_rows]
		seen_ids.update(new_ids)
		save_seen_ids(new_ids)

		total += len(matches)
		less_than_match_id = min(r["match_id"] for r in rows)
		save_last_match_id(less_than_match_id)
		print(f"Collected {total}/{target}")
		time.sleep(1)
