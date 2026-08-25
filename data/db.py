import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "matches.db")


def get_connection():
	connection = sqlite3.connect(DB_PATH)
	connection.row_factory = sqlite3.Row
	return connection


def commit_and_close(connection):
	connection.commit()
	connection.close()


def init_db():
	connection = get_connection()
	cursor = connection.cursor()

	#table of dry match data: picks, outcome, match_id
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS matches (
			match_id INTEGER PRIMARY KEY,
			seq_num INTEGER,
			radiant_win INTEGER,
			start_time INTEGER,
			patch TEXT,
			radiant_draft TEXT,
			dire_draft TEXT
		)
	""")

	#table for hero winrate per patch
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS hero_stats (
			hero_id INTEGER,
			patch INTEGER,
			winrate REAL,
			pickrate REAL,
			PRIMARY KEY (hero_id, patch)
		)
	""")

	commit_and_close(connection)


def insert_match(match_id, seq_num, radiant_win, start_time, radiant_draft, dire_draft):
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("""
		INSERT OR IGNORE INTO matches
		(match_id, seq_num, radiant_win, start_time, patch, radiant_draft, dire_draft)
		VALUES (?, ?, ?, ?, NULL, ?, ?)
	""", (
		match_id,
		seq_num,
		int(radiant_win),
		start_time,
		json.dumps(radiant_draft),
		json.dumps(dire_draft)
	))

	commit_and_close(connection)


def insert_hero_stat(hero_id, patch, winrate, pickrate):
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("""
		INSERT OR REPLACE INTO hero_stats
		(hero_id, patch, winrate, pickrate)
		VALUES (?, ?, ?, ?)
	""", (hero_id, patch, winrate, pickrate))

	commit_and_close(connection)


def get_match(match_id):
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
	row = cursor.fetchone()
	connection.close()
	return row


def get_all_matches(patch=None):
	connection = get_connection()
	cursor = connection.cursor()

	if patch:
		cursor.execute("SELECT * FROM matches WHERE patch = ?", (patch,))
	else:
		cursor.execute("SELECT * FROM matches")

	rows = cursor.fetchall()
	connection.close()
	return rows


def get_hero_stats(hero_id, patch=None):
	connection = get_connection()
	cursor = connection.cursor()

	if patch:
		cursor.execute("SELECT * FROM hero_stats WHERE hero_id = ? AND patch = ?", (hero_id, patch))
	else:
		cursor.execute("SELECT * FROM hero_stats WHERE hero_id = ?", (hero_id,))

	row = cursor.fetchone()
	connection.close()
	return row


def get_last_seq_num():
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("SELECT MAX(seq_num) FROM matches")
	row = cursor.fetchone()
	connection.close()
	return row[0] if row[0] else None


if __name__ == "__main__":
	init_db()
	print(f"DB initialized at {DB_PATH}")
