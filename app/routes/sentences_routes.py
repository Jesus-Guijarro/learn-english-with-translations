from flask import Blueprint, render_template, request, redirect, url_for
from app.database.db import create_connection
from datetime import date

# Blueprint setup
sentences_bp = Blueprint('sentences', __name__)

# Constants
NUM_SENTENCES_PER_LIST = 30
NUM_RECENT_RESULTS = 5
SHOW_RESULTS_PER_PAGE = 10

# Helper functions

def _get_last_sentence_settings():
    """Returns the last difficulty and list number from the exercises table, or defaults to (1,1)."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT difficulty, list_num FROM exercises ORDER BY date DESC LIMIT 1")
        row = cur.fetchone()
        return (row[0], row[1]) if row else (1, 1)


def _insert_exercise(difficulty, list_num):
    """Inserts a new exercise record and returns its ID."""
    today = date.today()
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO exercises (difficulty, list_num, num_errors, date) VALUES (?, ?, ?, ?)",
            (difficulty, list_num, 0, today)
        )
        conn.commit()
        return cur.lastrowid


def _fetch_sentences(difficulty, list_num):
    """Fetches sentences for a given difficulty and list number."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, spanish, english FROM sentences WHERE difficulty = ? AND list_num = ?",
            (difficulty, list_num)
        )
        return cur.fetchall()


def _fetch_recent_exercises(limit):
    """Fetches the most recent exercise results up to the given limit."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT difficulty, list_num, num_errors, date, id "
            "FROM exercises ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cur.fetchall()


def _get_last_exercise_id():
    """Returns the latest exercise ID from the exercises table, or None if none."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM exercises ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None


def _record_sentence_results(exercise_id, errors_data):
    """Inserts wrong translations for a given exercise."""
    with create_connection() as conn:
        cur = conn.cursor()
        for sentence_id, wrong_translation in errors_data:
            cur.execute(
                "INSERT INTO results (exercise_id, sentence_id, wrong_translation) VALUES (?, ?, ?)",
                (exercise_id, sentence_id, wrong_translation)
            )
        conn.commit()


def _fetch_results(exercise_id):
    """Fetches results (including wrong translations) for a specific exercise."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT s.difficulty, s.list_num, s.num, s.spanish, s.english, r.wrong_translation "
            "FROM sentences s JOIN results r ON s.id = r.sentence_id "
            "WHERE r.exercise_id = ?",
            (exercise_id,)
        )
        return cur.fetchall()


def _update_exercise_errors(exercise_id, num_errors):
    """Updates the number of errors for a given exercise."""
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE exercises SET num_errors = ? WHERE id = ?",
            (num_errors, exercise_id)
        )
        conn.commit()


# Routes

@sentences_bp.route('/sentences', methods=['GET', 'POST'])
def sentences():
    """Handles listing sentences and starting exercises."""
    if request.method == 'POST':
        action = request.form.get('action')
        difficulty = int(request.form['difficulty'])
        list_num = int(request.form['list_num'])
        if action == 'start_exercise':
            _insert_exercise(difficulty, list_num)
            return redirect(url_for('sentences.exercise', difficulty=difficulty, list_num=list_num))
        elif action == 'show_list':
            data = _fetch_sentences(difficulty, list_num)
            recent = _fetch_recent_exercises(NUM_RECENT_RESULTS)
            return render_template(
                'sentences.html', difficulty=difficulty, list_num=list_num,
                data=data, results_data=recent
            )
    difficulty, list_num = _get_last_sentence_settings()
    data = _fetch_sentences(difficulty, list_num)
    recent = _fetch_recent_exercises(NUM_RECENT_RESULTS)
    return render_template(
        'sentences.html', difficulty=difficulty, list_num=list_num,
        data=data, results_data=recent
    )

@sentences_bp.route('/exercise', methods=['GET', 'POST'])
def exercise():
    """Handles sentence translation exercise logic and recording results."""
    difficulty = request.args.get('difficulty', type=int)
    list_num = request.args.get('list_num', type=int)
    data = _fetch_sentences(difficulty, list_num)
    if request.method == 'POST':
        # Collect user translations
        translations = [
            request.form.get(f'translation_{i}') for i in range(1, NUM_SENTENCES_PER_LIST + 1)
        ]
        # Determine which translations are wrong
        errors = []
        for idx, row in enumerate(data):
            if row[2] != translations[idx]:
                errors.append((row[0], translations[idx]))
        # Record wrong translations
        exercise_id = _get_last_exercise_id()
        _record_sentence_results(exercise_id, errors)
        return redirect(url_for('sentences.exercise_results', exercise_id=exercise_id))
    return render_template(
        'exercise.html', difficulty=difficulty, list_num=list_num, data=data
    )

@sentences_bp.route('/exercise_results')
def exercise_results():
    """Displays results of the most recent sentence exercise and updates error count."""
    exercise_id = request.args.get('exercise_id', type=int)
    results = _fetch_results(exercise_id)
    num_errors = len(results)
    _update_exercise_errors(exercise_id, num_errors)
    return render_template('exercise_results.html', results=results)

@sentences_bp.route('/past_exercise_results')
def past_exercise_results():
    """Shows saved results for a specific exercise without updating counts."""
    exercise_id = request.args.get('exercise_id', type=int)
    exercise = _fetch_results(exercise_id)
    return render_template('past_exercise_results.html', exercise=exercise)

@sentences_bp.route('/show_results')
def show_results():
    """Paginates through past sentence exercises."""
    page = request.args.get('page', 1, type=int)
    per_page = SHOW_RESULTS_PER_PAGE
    offset = (page - 1) * per_page
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT difficulty, list_num, num_errors, date, id "
            "FROM exercises ORDER BY id DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        data = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM exercises")
        total_rows = cur.fetchone()[0]
    return render_template(
        'show_results.html', data=data, page=page,
        per_page=per_page, total_rows=total_rows
    )
