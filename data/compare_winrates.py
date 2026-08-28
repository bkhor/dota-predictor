import os
import sys

import requests

sys.path.append(os.path.dirname(__file__))
from db import get_connection

def fetch_opendota_winrates():
    heroes = requests.get("https://api.opendota.com/api/heroStats").json()
    winrates = {}
    for h in heroes:
        total = h.get("pub_pick", 0)
        wins = h.get("pub_win", 0)
        if total > 0:
            winrates[h["id"]] = (h["localized_name"], wins / total)
    return winrates

def fetch_my_winrates():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT hero_id, winrate FROM hero_stats WHERE patch = 0")
    rows = {row["hero_id"]: row["winrate"] for row in cursor.fetchall()}
    connection.close()
    return rows

def run():
    print("Fetching OpenDota hero stats...")
    opendota = fetch_opendota_winrates()
    my = fetch_my_winrates()

    print(f"\n{'Hero':<25} {'my':>8} {'OpenDota':>10} {'Diff':>8}")
    print("-" * 55)

    diffs = []
    for hero_id, (name, od_wr) in sorted(opendota.items()):
        if hero_id not in my:
            continue
        my_wr = my[hero_id]
        diff = my_wr - od_wr
        diffs.append(abs(diff))
        print(f"{name:<25} {my_wr:>8.3f} {od_wr:>10.3f} {diff:>+8.3f}")

    if diffs:
        print(f"\nMean absolute difference: {sum(diffs)/len(diffs):.4f}")
        print(f"Max difference: {max(diffs):.4f}")

if __name__ == "__main__":
    run()
