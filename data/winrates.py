import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from db import get_all_matches, insert_hero_stat


def compute_winrates(matches):
    wins = defaultdict(int)
    picks = defaultdict(int)

    for match in matches:
        radiant_win = match["radiant_win"]
        radiant_draft = json.loads(match["radiant_draft"])
        dire_draft = json.loads(match["dire_draft"])

        for hero_id in radiant_draft:
            picks[hero_id] += 1
            if radiant_win:
                wins[hero_id] += 1

        for hero_id in dire_draft:
            picks[hero_id] += 1
            if not radiant_win:
                wins[hero_id] += 1

    return {
        hero_id: wins[hero_id] / picks[hero_id]
        for hero_id in picks
    }, picks


def run(patch=None):
    matches = get_all_matches(patch=patch)
    print(f"Computing winrates from {len(matches)} matches (patch={patch or 'all'})")

    winrates, picks = compute_winrates(matches)

    for hero_id, winrate in winrates.items():
        total = picks[hero_id]
        pickrate = total / len(matches)
        insert_hero_stat(hero_id, patch or 0, winrate, pickrate)

    print(f"Stored winrates for {len(winrates)} heroes")


if __name__ == "__main__":
    run()
