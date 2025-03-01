import pandas as pd

df = pd.read_csv('awakened_music.csv')
df

import sqlite3
import pandas as pd

conn = sqlite3.connect("awakened_songs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE songs (
    [index] INTEGER PRIMARY KEY,
    title TEXT,
    url TEXT
)
""")

conn.commit()

for i, row in df.iterrows():
    cursor.execute("INSERT INTO songs ([index], title, url) VALUES (?, ?, ?)", (i, row["title"], row["url"]))

conn.commit()

df = pd.read_sql("SELECT * FROM songs", conn)

conn.close()

df
