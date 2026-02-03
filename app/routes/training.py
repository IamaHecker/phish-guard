from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Result

bp = Blueprint('training', __name__)

@bp.route('/training/<token>')
def landing(token):
    result = Result.query.filter_by(token=token).first_or_404()
    if not result.clicked:
        result.clicked = True
        db.session.commit()
    return render_template('training/landing.html', token=token)

@bp.route('/training/<token>/quiz', methods=['GET', 'POST'])
def quiz(token):
    result = Result.query.filter_by(token=token).first_or_404()
    if request.method == 'POST':
        # Check all 5 answers
        answers = {
            'q1': request.form.get('q1'),
            'q2': request.form.get('q2'),
            'q3': request.form.get('q3'),
            'q4': request.form.get('q4'),
            'q5': request.form.get('q5')
        }
        
        # Verify all are 'correct'
        import json
        result.quiz_answers = json.dumps(answers)
        
        if all(a == 'correct' for a in answers.values()):
            result.quiz_passed = True
            db.session.commit()
            flash('Congratulations! You passed the phishing quiz.')
            return redirect(url_for('main.index'))
        else:
            db.session.commit() # Save answers even if failed
            flash('You missed some questions. Review the answers and try again.')
    
    return render_template('training/quiz.html', token=token)
