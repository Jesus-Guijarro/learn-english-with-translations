import sqlite3
import pandas as pd

# Connect to or create the SQLite database
conn = sqlite3.connect('lists.db')
cur = conn.cursor()

# ---------------------
# TABLE DEFINITIONS
# ---------------------

# Table of translation exercises (sentence-based)
cur.execute('''
    CREATE TABLE sentences (
        id INTEGER PRIMARY KEY,
        difficulty INTEGER,
        list_num INTEGER,
        num INTEGER,
        spanish TEXT,
        english TEXT
    )
''')

# Records each session (attempt) of a translation exercise
cur.execute('''
    CREATE TABLE exercises (
        id INTEGER PRIMARY KEY,
        difficulty INTEGER,
        list_num INTEGER,
        num_errors INTEGER,
        date DATE
    )
''')

# Stores sentence-level results (one row per incorrect sentence)
cur.execute('''
    CREATE TABLE results (
        exercise_id INTEGER,
        sentence_id INTEGER,
        wrong_translation VARCHAR(255),
        PRIMARY KEY (exercise_id, sentence_id),
        FOREIGN KEY (exercise_id) REFERENCES exercises(id),
        FOREIGN KEY (sentence_id) REFERENCES sentences(id)
    )
''')

# ---------------------
# IRREGULAR VERBS
# ---------------------

# Stores all irregular verbs
cur.execute('''
    CREATE TABLE IF NOT EXISTS irregular_verbs (
        id INTEGER PRIMARY KEY,
        spanish TEXT,
        infinitive TEXT,
        past TEXT,
        participle TEXT,
        times_asked INTEGER DEFAULT 0,
        times_failed INTEGER DEFAULT 0
    )
''')

# One row per user exercise session (10 verbs)
cur.execute('''
    CREATE TABLE IF NOT EXISTS exercises_irregular_verbs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_verbs INT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Each row links an exercise session with a specific verb the user got wrong
cur.execute('''
    CREATE TABLE results_irregular_verbs (
        result_id INTEGER,
        verb_id INTEGER,
        PRIMARY KEY (result_id, verb_id),
        FOREIGN KEY (result_id) REFERENCES exercises_irregular_verbs(id),
        FOREIGN KEY (verb_id) REFERENCES irregular_verbs(id)
    )
''')

# ---------------------
# PHRASAL VERBS
# ---------------------

# Stores all phrasal verbs
cur.execute('''
    CREATE TABLE IF NOT EXISTS phrasal_verbs (
        id INTEGER PRIMARY KEY,
        english TEXT,
        spanish TEXT,
        times_asked INTEGER DEFAULT 0,
        times_failed INTEGER DEFAULT 0
    )
''')

# One row per user exercise session (20 verbs)
cur.execute('''
    CREATE TABLE IF NOT EXISTS exercises_phrasal_verbs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_verbs INT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Each row links an exercise session with a specific phrasal verb the user got wrong
cur.execute('''
    CREATE TABLE results_phrasal_verbs (
        result_id INTEGER,
        verb_id INTEGER,
        PRIMARY KEY (result_id, verb_id),
        FOREIGN KEY (result_id) REFERENCES exercises_phrasal_verbs(id),
        FOREIGN KEY (verb_id) REFERENCES phrasal_verbs(id)
    )
''')

# ---------------------
# DATA INSERTION FUNCTIONS
# ---------------------

def insert_irregular_verbs_data(filename):
    # Loads irregular verbs from Excel and initializes counters
    df = pd.read_excel(filename)
    df['times_asked'] = 0
    df['times_failed'] = 0
    df.to_sql('irregular_verbs', conn, if_exists='append', index=False)

def insert_phrasal_verbs_data(filename):
    # Loads phrasal verbs from Excel and initializes counters
    df = pd.read_excel(filename)
    df['times_asked'] = 0
    df['times_failed'] = 0
    df.to_sql('phrasal_verbs', conn, if_exists='append', index=False)


# ---------------------
# INITIAL DATA INSERTION
# ---------------------

archivo_excel = 'lists.xlsx'
df = pd.read_excel(archivo_excel)

columnas_deseadas = ['Dificultad', 'Lista', 'Número', 'Español', 'Inglés']

try:
    # Insert all sentence translations into the database
    for index, row in df.iterrows():
        query = """
        INSERT INTO sentences (id, difficulty, list_num, num, spanish, english)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (None, row['Dificultad'], row['Lista'], row['Número'], row['Español'], row['Inglés'])
        cur.execute(query, values)

    conn.commit()
    print("Data from lists.xlsx inserted successfully.")

    # Insert irregular and phrasal verbs
    insert_irregular_verbs_data('irregularverbs.xlsx')
    insert_phrasal_verbs_data('phrasalverbs.xlsx')
    conn.commit()
    print("Data from irregularverbs.xlsx and phrasalverbs.xlsx inserted successfully.")

except Exception as e:
    print(f"Error inserting data into SQLite: {str(e)}")

finally:
    cur.close()
    conn.close()
