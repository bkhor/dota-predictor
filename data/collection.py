import requests
from dataclasses import dataclass
import to_json

BASE_OPENDOTA_EXPLORER_API_URL = "https://api.opendota.com/api/explorer"
OUTPUT_FOLDER = "collected_matches"

@dataclass
class Match:
	radiant_win: bool
	radiant_draft: list
	dire_draft: list


def fetch_batch(less_than_match_id):
	sql = f"""
        SELECT match_id, radiant_win, picks_bans, version
        FROM matches
        WHERE picks_bans IS NOT NULL
        AND version = 22
        AND match_id < {less_than_match_id}
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




if __name__ == "__main__":
	rows = fetch_batch(999999999999)
	print(f"Got {len(rows)} rows")
	matches = parse_batch(rows)
	print(f"Parsed {len(matches)} valid matches")
	to_json(matches)
