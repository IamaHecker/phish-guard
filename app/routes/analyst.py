from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Campaign, Result

bp = Blueprint('analyst', __name__)

@bp.before_request
def restrict_to_analyst():
    if not current_user.is_authenticated or current_user.role != 'analyst':
        flash('Access denied. Analyst privileges required.')
        return redirect(url_for('main.index'))

@bp.route('/export/<int:campaign_id>')
@login_required
def export_campaign(campaign_id):
    import csv
    import io
    from flask import Response
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Email', 'Msg Sent', 'Opened', 'Clicked', 'Reported', 'Quiz Passed', 'Token'])
    
    # Data
    for result in campaign.results:
        # User might be deleted, handle securely
        email = result.user.email if result.user else "Unknown"
        writer.writerow([
            email,
            result.sent,
            result.opened,
            result.clicked,
            result.reported,
            result.quiz_passed,
            result.token
        ])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=campaign_{campaign_id}_report.csv"}
    )

@bp.route('/dashboard')
@login_required
def dashboard():
    campaigns = Campaign.query.all()
    from app.models import User
    
    # Simple stats calculation
    total_campaigns = len(campaigns)
    total_results = Result.query.count()
    opened_count = Result.query.filter_by(opened=True).count()
    clicked_count = Result.query.filter_by(clicked=True).count()
    passed_count = Result.query.filter_by(quiz_passed=True).count()
    
    # --- CYBER SCORE & RISK ANALYSIS ---
    users = User.query.filter(User.role != 'admin', User.role != 'analyst').all()
    user_scores = []
    
    for user in users:
        score = 100
        user_results = Result.query.filter_by(user_id=user.id).all()
        
        for r in user_results:
            if r.clicked:
                score -= 15 # Heavy penalty for clicking
            if r.reported:
                score += 10 # Bonus for vigilant reporting
            if r.quiz_passed:
                score += 5  # Restoration for learning
        
        # Clamp score
        score = max(0, min(100, score))
        
        user_scores.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'score': score,
            'campaigns': len(user_results)
        })
        
    # Sort: Lowest score = Highest Risk
    user_scores.sort(key=lambda x: x['score'])
    
    # Filter: Only show users who actually have a risk (score < 100)
    high_risk_users = [u for u in user_scores if u['score'] < 100][:10]
    
    # --- AUTOMATED RECOMMENDATIONS ---
    recommendations = []
    
    if total_results > 0:
        click_rate = (clicked_count / total_results) * 100
        if click_rate > 15:
            recommendations.append({
                'level': 'danger',
                'title': 'High Organizational Risk',
                'text': f'Global click rate is {click_rate:.1f}%. Immediate remedial training assigned is recommended.'
            })
        elif click_rate < 5:
            recommendations.append({
                'level': 'success',
                'title': 'Strong Security Posture',
                'text': 'Click rate is low. Continue positive reinforcement campaigns.'
            })
            
    if passed_count > 0 and clicked_count > 0:
        train_rate = (passed_count / clicked_count) * 100
        if train_rate < 60:
             recommendations.append({
                'level': 'warning',
                'title': 'Training Completion Gap',
                'text': f'Only {train_rate:.1f}% of victims completed the quiz. Simplify the training content.'
            })
            
    return render_template('analyst/dashboard.html', 
                           campaigns=campaigns, 
                           total_campaigns=total_campaigns,
                           total_results=total_results,
                           opened_count=opened_count,
                           clicked_count=clicked_count,
                           passed_count=passed_count,
                           high_risk_users=high_risk_users,
                           recommendations=recommendations)

@bp.route('/api/stats')
@login_required
def get_stats():
    total_campaigns = Campaign.query.count()
    total_results = Result.query.count()
    opened_count = Result.query.filter_by(opened=True).count()
    clicked_count = Result.query.filter_by(clicked=True).count()
    passed_count = Result.query.filter_by(quiz_passed=True).count()
    
    return jsonify({
        'total_campaigns': total_campaigns,
        'total_results': total_results,
        'opened_count': opened_count,
        'clicked_count': clicked_count,
        'passed_count': passed_count
    })

@bp.route('/reset_score/<int:user_id>', methods=['POST'])
@login_required
def reset_score(user_id):
    from app.models import User
    from app import db
    
    user = User.query.get_or_404(user_id)
    
    # Reset score by deleting all negative results for this user?
    # Or just deleting all results for this user to give them a clean slate.
    # The user requested "Delete the high risk employees", which implies clearing their record.
    
    try:
        # Delete all results associated with this user
        # Using explicit deletion to ensure it commits correctly
        results = Result.query.filter_by(user_id=user.id).all()
        for r in results:
            db.session.delete(r)
            
        db.session.commit()
        flash(f'Successfully reset cyber score for {user.username}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error resetting user score', 'danger')
        
    return redirect(url_for('analyst.dashboard'))

@bp.route('/reset_all_scores', methods=['POST'])
@login_required
def reset_all_scores():
    from app.models import User
    from app import db
    
    try:
        # Delete ALL results to reset everyone's score
        db.session.query(Result).delete()
        db.session.commit()
        flash('Successfully reset ALL employee cyber scores.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error resetting all scores', 'danger')
        
    return redirect(url_for('analyst.dashboard'))
