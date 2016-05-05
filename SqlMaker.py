import sqlite3

def make_tables(filepath):
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()

    cur.execute(''' CREATE TABLE Tournament
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         name TEXT,
         date TEXT)''')

    cur.execute(''' CREATE TABLE Teams
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         name TEXT,
         tournament_id INTEGER)''')

    cur.execute(''' CREATE TABLE Players
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         first_name TEXT,
         last_name TEXT,
         nickname TEXT,
         phone TEXT)''')

    cur.execute(''' CREATE TABLE PlayersToTeams
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         team_id INTEGER REFERENCES Teams(id),
         player_id INTEGER REFERENCES Players(id))''')

    cur.execute(''' CREATE TABLE PlayersToTournaments
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         tournament_id INTEGER REFERENCES Tournaments(id),
         player_id INTEGER REFERENCES Players(id))''')

def main():
    make_tables("testdb_.db")

if __name__ == "__main__":
    main()
    
