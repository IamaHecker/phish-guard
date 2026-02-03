from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/track/open/<token>')
def track_open(token):
    from app.models import Result
    from app import db
    from datetime import datetime
    import io
    from flask import send_file
    
    result = Result.query.filter_by(token=token).first()
    if result and not result.opened:
        result.opened = True
        # If timestamp wasn't set (e.g. sent time), set it now. 
        # But usually we want 'opened_at'. The model has 'timestamp' which seems to be generic.
        # Let's just update the record.
        db.session.commit()
        
    # Return 1x1 transparent pixel
    return send_file(io.BytesIO(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'), mimetype='image/gif')

@bp.route('/track/click/<token>')
def track_click(token):
    from app.models import Result
    from app import db
    from flask import redirect, url_for
    
    result = Result.query.filter_by(token=token).first()
    if result:
        if not result.clicked:
            result.clicked = True
            result.opened = True # If they clicked, they must have opened
            db.session.commit()
            db.session.commit()
        return redirect(url_for('training.landing', token=result.token))
    return redirect(url_for('main.index'))
