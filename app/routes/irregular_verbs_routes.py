from flask import Blueprint, render_template, request, redirect, url_for
from app.database.db import create_connection

# Constants
NUM_IRREGULAR_VERBS = 10

irregular_verbs_bp = Blueprint('irregular_verbs', __name__, url_prefix='/irregular_verbs')

@irregular_verbs_bp.route('/', methods=['GET', 'POST'])
def index():
    """Display paginated irregular verbs or redirect to exercise for chosen group."""
    if request.method == 'POST':
        group = request.form.get('group_verbs', type=int)
        offset = (group - 1) * NUM_IRREGULAR_VERBS
        return redirect(url_for('irregular_verbs.exercise', group_verbs=group, offset=offset))

    page = request.args.get('page', 1, type=int)
    per_page = NUM_IRREGULAR_VERBS
    offset = (page - 1) * per_page

    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT spanish, infinitive, past, participle, times_asked, times_failed "
            "FROM irregular_verbs LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        data = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM irregular_verbs")
        total_rows = cur.fetchone()[0]
        cur.execute(
            "SELECT group_verbs FROM exercises_irregular_verbs ORDER BY id DESC LIMIT 1"
        )
        last = cur.fetchone()
        group = last[0] if last else 1

    return render_template(
        'irregular_verbs.html', data=data,
        page=page, per_page=per_page, total_rows=total_rows,
        group_verbs=group
    )

@irregular_verbs_bp.route('/exercise', methods=['GET', 'POST'])
def exercise():
    """Handle exercise display, answer checking, and stats update for irregular verbs."""
    # Ensure group and offset have sensible defaults
    group = request.args.get('group_verbs', default=1, type=int)
    offset = request.args.get('offset', type=int)
    if offset is None:
        offset = (group - 1) * NUM_IRREGULAR_VERBS

    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, spanish, infinitive, past, participle FROM irregular_verbs "
            "ORDER BY id LIMIT ? OFFSET ?",
            (NUM_IRREGULAR_VERBS, offset)
        )
        data = cur.fetchall()

        if request.method == 'POST':
            errors, failed_ids = [], []
            for idx, (vid, _, inf, past, part) in enumerate(data, start=1):
                user = (
                    request.form.get(f'infinitive_{idx}'),
                    request.form.get(f'past_{idx}'),
                    request.form.get(f'participle_{idx}')
                )
                expected = (inf, past, part)
                if user != expected:
                    errors.append(idx)
                    failed_ids.append(vid)
                    cur.execute(
                        "UPDATE irregular_verbs SET times_failed = times_failed + 1 WHERE id = ?", (vid,)
                    )
                cur.execute(
                    "UPDATE irregular_verbs SET times_asked = times_asked + 1 WHERE id = ?", (vid,)
                )

            cur.execute(
                "INSERT INTO exercises_irregular_verbs (group_verbs) VALUES (?)", (group,)
            )
            result_id = cur.lastrowid
            for vid in failed_ids:
                cur.execute(
                    "INSERT INTO results_irregular_verbs (result_id, verb_id) VALUES (?, ?)", (result_id, vid)
                )
            conn.commit()
            return render_template(
                'exercise_irregular_verbs.html', data=data,
                group_verbs=group, offset=offset,
                exercise_done=True, errors=errors
            )

    # GET shows blank exercise form
    return render_template(
        'exercise_irregular_verbs.html', data=data,
        group_verbs=group, offset=offset,
        exercise_done=False, errors=[]
    )