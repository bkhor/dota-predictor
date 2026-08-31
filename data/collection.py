import os
import time
from dataclasses import dataclass

import requests
from db import get_last_seq_num, init_db, insert_match
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

STEAM_API_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/"
INITIAL_SEQ_NUM = 6700000000  #2024ish 

@dataclass
class Match:
	match_id: int
	seq_num: int
	radiant_win: bool
	start_time: int
	radiant_draft: list
	dire_draft: list


def fetch_batch(seq_num, batch_size=100):
	params = {
		"key": STEAM_API_KEY,
		"start_at_match_seq_num": seq_num,
		"matches_requested": batch_size
	}
	for attempt in range(5):
		response = requests.get(STEAM_API_URL, params=params)
		if response.status_code == 429:
			wait = 2 ** attempt * 5
			print(f"Rate limited. Waiting {wait}s...")
			time.sleep(wait)
			continue
		response.raise_for_status()
		return response.json()["result"]["matches"]
	raise RuntimeError("Failed after 5 retries")


def parse_match(raw):
	if not raw.get("picks_bans"):
		return None

	picks = [p for p in raw["picks_bans"] if p["is_pick"]]
	radiant_picks = [p["hero_id"] for p in picks if p["team"] == 0]
	dire_picks = [p["hero_id"] for p in picks if p["team"] == 1]

	if len(radiant_picks) != 5 or len(dire_picks) != 5:
		return None

	return Match(
		match_id=raw["match_id"],
		seq_num=raw["match_seq_num"],
		radiant_win=raw["radiant_win"],
		start_time=raw["start_time"],
		radiant_draft=radiant_picks,
		dire_draft=dire_picks
	)


def get_match_count():
	from db import get_connection
	connection = get_connection()
	cursor = connection.cursor()
	cursor.execute("SELECT COUNT(*) FROM matches")
	count = cursor.fetchone()[0]
	connection.close()
	return count


def run(target=150000):
	init_db()
	seq_num = get_last_seq_num() or INITIAL_SEQ_NUM
	total = get_match_count()
	print(f"Resuming from {total} existing matches")

	while total < target:
		rows = fetch_batch(seq_num)
		if not rows:
			break

		for raw in rows:
			match = parse_match(raw)
			if match:
				insert_match(
					match.match_id,
					match.seq_num,
					match.radiant_win,
					match.start_time,
					match.radiant_draft,
					match.dire_draft
				)
				total += 1

		seq_num = max(r["match_seq_num"] for r in rows) + 1
		print(f"Collected {total}/{target} | seq_num: {seq_num}")
		time.sleep(2)


if __name__ == "__main__":
	run()
