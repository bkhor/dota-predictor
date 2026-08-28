import json
import time

import requests
from db import commit_and_close, get_connection, init_db

PATCHLIST_URL = "https://www.dota2.com/datafeed/patchnoteslist?language=english"
PATCHNOTES_URL = "https://www.dota2.com/datafeed/patchnotes?language=english&version={}"


def fetch_all_versions():
    data = requests.get(PATCHLIST_URL).json()
    return [(p["patch_number"], p["patch_timestamp"]) for p in data["patches"]]


def fetch_notes(version):
    return requests.get(PATCHNOTES_URL.format(version)).json()


def insert_patch(version, timestamp, data):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO patches (version, timestamp, data) VALUES (?, ?, ?)",
        (version, timestamp, json.dumps(data)),
    )
    commit_and_close(connection)


def assign_patches():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT version, timestamp FROM patches ORDER BY timestamp ASC")
    patch_list = cursor.fetchall()

    for i, (version, ts_start) in enumerate(patch_list):
        ts_end = patch_list[i + 1][1] if i + 1 < len(patch_list) else 9999999999
        cursor.execute(
            "UPDATE matches SET patch = ? WHERE start_time >= ? AND start_time < ?",
            (version, ts_start, ts_end),
        )

    commit_and_close(connection)
    print("Patch assignment done")


def run():
    init_db()
    versions = fetch_all_versions()
    for version, timestamp in versions:
        notes = fetch_notes(version)
        insert_patch(version, timestamp, notes)
        print(f"Fetched {version}")
        time.sleep(0.3)
    assign_patches()


if __name__ == "__main__":
    run()
