from flask import Blueprint, render_template
from app.database.db import create_connection

main_bp = Blueprint('main', __name__)

def _get_latest_exercise_id(table_name):
    """Returns the latest exercise ID from the given table, or None if there are none."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM {table_name} ORDER BY date DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None


def _fetch_latest_sentence_errors():
    """Fetches errors (incorrectly translated sentences) from the most recent sentences exercise."""
    with create_connection() as conn:
        cur = conn.cursor()
        # Get the most recent exercise date
        cur.execute("SELECT MAX(date) FROM exercises")
        row = cur.fetchone()
        if not row or not row[0]:
            return []
        last_date = row[0]
        # Retrieve all exercise IDs for that date
        cur.execute("SELECT id FROM exercises WHERE date = ?", (last_date,))
        exercise_ids = [r[0] for r in cur.fetchall()]
        errors = []
        # Collect all error records
        query = (
            "SELECT s.difficulty, s.list_num, s.num, s.spanish, s.english, r.wrong_translation "
            "FROM sentences s "
            "JOIN results r ON s.id = r.sentence_id "
            "WHERE r.exercise_id = ?"
        )
        for eid in exercise_ids:
            cur.execute(query, (eid,))
            errors.extend(cur.fetchall())
        return errors


def _fetch_failed_items(data_table, exercise_table, results_table, id_field, columns):
    """Fetches failed items for a generic verbs table from the most recent exercise."""
    latest_ex_id = _get_latest_exercise_id(exercise_table)
    if not latest_ex_id:
        return []
    with create_connection() as conn:
        cur = conn.cursor()
        # Retrieve IDs of failed items
        cur.execute(f"SELECT {id_field} FROM {results_table} WHERE result_id = ?", (latest_ex_id,))
        failed_ids = [r[0] for r in cur.fetchall()]
        if not failed_ids:
            return []
        # Build placeholders for SQL IN clause
        placeholders = ','.join('?' * len(failed_ids))
        cols = ', '.join(columns)
        query = f"SELECT {cols} FROM {data_table} WHERE id IN ({placeholders})"
        cur.execute(query, failed_ids)
        return cur.fetchall()

@main_bp.route('/')
def home():
    sentences = _fetch_latest_sentence_errors()
    irregular_verbs = _fetch_failed_items(
        data_table='irregular_verbs',
        exercise_table='exercises_irregular_verbs',
        results_table='results_irregular_verbs',
        id_field='verb_id',
        columns=['spanish', 'infinitive', 'past', 'participle', 'times_asked', 'times_failed']
    )
    phrasal_verbs = _fetch_failed_items(
        data_table='phrasal_verbs',
        exercise_table='exercises_phrasal_verbs',
        results_table='results_phrasal_verbs',
        id_field='verb_id',
        columns=['spanish', 'english', 'times_asked', 'times_failed']
    )
    return render_template(
        'home.html',
        sentences=sentences,
        irregular_verbs=irregular_verbs,
        phrasal_verbs=phrasal_verbs
    )