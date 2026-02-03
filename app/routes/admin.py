from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Campaign, Template
from app.forms import CampaignForm # Need to create this

bp = Blueprint('admin', __name__)

@bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Access denied. Admins only.')
        return redirect(url_for('main.index'))

@bp.route('/campaigns')
@login_required
def campaigns():
    campaigns_data = []
    all_campaigns = Campaign.query.all()
    
    for campaign in all_campaigns:
        stats = {
            'sent': campaign.results.filter_by(sent=True).count(),
            'opened': campaign.results.filter_by(opened=True).count(),
            'clicked': campaign.results.filter_by(clicked=True).count(),
            'total': campaign.results.count()
        }
        campaigns_data.append({
            'campaign': campaign,
            'stats': stats
        })
        
    return render_template('admin/campaigns.html', campaigns=campaigns_data)

@bp.route('/campaign/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    # Populate templates choice
    form.template.choices = [(t.id, t.name) for t in Template.query.all()]
    
    if form.validate_on_submit():
        campaign = Campaign(name=form.name.data, template_id=form.template.data, target_emails=form.targets.data)
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign created successfully.')
        return redirect(url_for('admin.campaigns'))
    return render_template('admin/create_campaign.html', form=form)

@bp.route('/templates')
@login_required
def templates():
    templates = Template.query.all()
    return render_template('admin/templates.html', templates=templates)

@bp.route('/template/create', methods=['GET', 'POST'])
@login_required
def create_template():
    from app.forms import TemplateForm
    form = TemplateForm()
    if form.validate_on_submit():
        template = Template(name=form.name.data, subject=form.subject.data, body=form.body.data, landing_page_id=form.landing_page_id.data)
        db.session.add(template)
        db.session.commit()
        flash('Template created successfully.')
        return redirect(url_for('admin.templates'))
    return render_template('admin/create_template.html', form=form, title="Create Template")

@bp.route('/template/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    from app.forms import TemplateForm
    template = Template.query.get_or_404(id)
    form = TemplateForm(obj=template)
    if form.validate_on_submit():
        template.name = form.name.data
        template.subject = form.subject.data
        template.body = form.body.data
        template.landing_page_id = form.landing_page_id.data
        db.session.commit()
        flash('Template updated successfully.')
        return redirect(url_for('admin.templates'))
    return render_template('admin/create_template.html', form=form, title="Edit Template")

@bp.route('/template/<int:id>/delete', methods=['POST'])
@login_required
def delete_template(id):
    template = Template.query.get_or_404(id)
    # Check if used in campaigns? For now, let's allow delete but maybe warn? 
    # Simply delete for now.
    db.session.delete(template)
    db.session.commit()
    flash('Template deleted successfully.')
    return redirect(url_for('admin.templates'))

@bp.route('/template/<int:id>/preview')
@login_required
def preview_template(id):
    template = Template.query.get_or_404(id)
    return render_template('admin/preview_template.html', template=template)

@bp.route('/campaign/<int:id>/launch')
@login_required
def launch_campaign(id):
    from app.models import User, Result
    from app.email import send_email
    from email_validator import validate_email, EmailNotValidError
    
    campaign = Campaign.query.get_or_404(id)
    if campaign.status != 'draft':
        flash('Campaign already launched.')
        return redirect(url_for('admin.campaigns'))
        
    target_list = [email.strip() for email in campaign.target_emails.split(',') if email.strip()] if campaign.target_emails else []
    
    users = []
    if target_list:
        # Send to specific targets
        for email in target_list:
            try:
                # Validate email
                valid = validate_email(email)
                email = valid.email
                
                user = User.query.filter_by(email=email).first()
                if not user:
                    # Create temporary user for target
                    username = email.split('@')[0]
                    user = User(username=username, email=email, role='target')
                    user.set_password('target123') # Random password in reality
                    db.session.add(user)
                    db.session.commit() # Commit to get ID
                users.append(user)
            except EmailNotValidError as e:
                flash(f"Skipping invalid email: {email} ({str(e)})")
                continue
    else:
        # Fallback to all non-admin users if no specific targets
        users = User.query.filter(User.role != 'admin').all() 
    
    sent_count = 0
    
    import uuid # Import uuid

    for user in users:
        result = Result(campaign_id=campaign.id, user_id=user.id, token=str(uuid.uuid4()))
        db.session.add(result)
        db.session.commit() # Commit to get ID
        
        # Prepare email
        template = Template.query.get(campaign.template_id)
        tracking_pixel = f'<img src="{url_for("main.track_open", token=result.token, _external=True)}" width="1" height="1" />'
        tracking_link = url_for("main.track_click", token=result.token, _external=True)
        
        # Simple replacement for placeholders
        body = template.body.replace('{{link}}', tracking_link)
        body = body.replace('{{name}}', user.username) # Personalization
        body += tracking_pixel
        
        sender = current_app.config.get('MAIL_USERNAME') or 'security@phishguard.com'
        if send_email(template.subject, sender, [user.email], body, body):
            result.sent = True
            sent_count += 1
        else:
            result.sent = False
        
        db.session.commit()
        
    campaign.status = 'running'
    db.session.commit()
    
    if sent_count < len(users):
        flash(f'Campaign launched with warnings! Sent to {sent_count} of {len(users)} users. Check server logs.')
    else:
        flash(f'Campaign launched! Sent to {sent_count} users.')
    return redirect(url_for('admin.campaigns'))

@bp.route('/campaign/<int:id>/delete', methods=['POST'])
@login_required
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    # Delete associated results first
    for result in campaign.results:
        db.session.delete(result)
        
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully.')
    return redirect(url_for('admin.campaigns'))

@bp.route('/campaign/<int:id>/report')
@login_required
def campaign_report(id):
    from app.models import Campaign, Result
    import json
    
    campaign = Campaign.query.get_or_404(id)
    results = campaign.results.all()
    
    # Initialize stats
    stats = {
        'total': len(results),
        'clicked': sum(1 for r in results if r.clicked),
        'passed': sum(1 for r in results if r.quiz_passed),
    }
    
    # Question Breakdown
    # q_stats = {'q1': {'correct': 0, 'wrong': 0}, ...}
    q_stats = {f'q{i}': {'correct': 0, 'wrong': 0, 'total': 0} for i in range(1, 6)}
    
    for r in results:
        if r.quiz_answers:
            try:
                answers = json.loads(r.quiz_answers)
                for q_key, answer_val in answers.items():
                    if q_key in q_stats:
                        q_stats[q_key]['total'] += 1
                        if answer_val == 'correct':
                            q_stats[q_key]['correct'] += 1
                        else:
                            q_stats[q_key]['wrong'] += 1
            except:
                pass # skip invalid json

    return render_template('admin/campaign_report.html', campaign=campaign, stats=stats, q_stats=q_stats)

@bp.route('/api/campaigns/stats')
@login_required
def campaign_stats_api():
    from app.models import Campaign
    from flask import jsonify
    
    campaigns = Campaign.query.all()
    data = []
    
    for c in campaigns:
        total = c.results.count()
        opened = c.results.filter_by(opened=True).count()
        clicked = c.results.filter_by(clicked=True).count()
        open_rate = int((opened / total * 100)) if total > 0 else 0
        
        data.append({
            'id': c.id,
            'status': c.status,
            'open_rate': open_rate,
            'clicked_count': clicked
        })
        
    return jsonify(data)
