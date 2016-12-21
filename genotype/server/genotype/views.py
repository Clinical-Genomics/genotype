# -*- coding: utf-8 -*-
import logging
import os

from flask import (abort, Blueprint, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import login_required
from werkzeug import secure_filename

from genotype.match.core import check_sample
from genotype.load.excel import load_excel
from genotype.store.models import Analysis, Sample, Plate
from genotype.server.ext import db
from genotype.store import api
from genotype.load.plate import extract_plateid


logger = logging.getLogger(__name__)
genotype_bp = Blueprint('genotype', __name__, template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/genotype')


@genotype_bp.route('/dashboard')
@login_required
def dashboard():
    """Display all samples."""
    pending, failing = api.pending(), api.failing()
    return render_template('genotype/dashboard.html', pending=pending,
                           failing=failing, query=request.args.get('query'))


@genotype_bp.route('/samples/<sample_id>')
@login_required
def sample(sample_id):
    """Display information about a sample."""
    sample_obj = sample_or_404(sample_id)
    return render_template('genotype/sample.html', sample=sample_obj)


@genotype_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload an Excel report file from MAF."""
    include_key = current_app.config['GENOTYPE_INCLUDE_KEY']
    req_file = request.files['excel']
    filename = secure_filename(req_file.filename)
    if not req_file or not filename.endswith('.xlsx'):
        return abort(500, 'Please select an Excel book for upload')
    if not current_app.config.get('GENOTYPE_NO_SAVE'):
        excel_path = os.path.join(current_app.config['GENOTYPE_GENOTYPE_DIR'],
                                  filename)
        req_file.save(excel_path)

    plate_id = extract_plateid(excel_path)
    new_plate = Plate(plate_id=plate_id)
    analyses = load_excel(filename, req_file.stream.read(),
                          include_key=include_key)
    for analysis in analyses:
        loaded_analysis = api.add_analysis(db, analysis, replace=True)
        if loaded_analysis:
            flash("added: {}".format(analysis.sample.id), 'info')
            new_plate.analyses.append(analysis)
    db.commit()

    return redirect(url_for('.dashboard'))


@genotype_bp.route('/check', methods=['POST'])
@genotype_bp.route('/check/<sample_id>', methods=['POST'])
@login_required
def check(sample_id=None):
    """Check samples."""
    if sample_id:
        samples = [sample_or_404(sample_id)]
        url = url_for('.sample', sample_id=sample_id)
    else:
        # fetch all pending samples
        samples = api.pending()
        url = url_for('.dashboard')

    for sample in samples:
        cutoffs = dict(max_nocalls=current_app.config['GENOTYPE_MAX_NOCALLS'],
                       max_mismatch=current_app.config['GENOTYPE_MAX_MISMATCH'],
                       min_matches=current_app.config['GENOTYPE_MIN_MATCHES'],)
        results = check_sample(sample, **cutoffs)
        sample.status = 'fail' if 'fail' in results.values() else 'pass'
    db.commit()
    return redirect(url)


@genotype_bp.route('/update/<sample_id>', methods=['POST'])
@login_required
def update(sample_id):
    """Update information about a sample."""
    sample_obj = sample_or_404(sample_id)
    sample_obj.sex = request.form['sample_sex'] or None
    sample_obj.comment = request.form.get('comment')
    for analysis in sample_obj.analyses:
        analysis.sex = request.form["{}_sex".format(analysis.type)] or None
    db.commit()
    return redirect(url_for('.sample', sample_id=sample_id))


@genotype_bp.route('/update-status/<sample_id>', methods=['POST'])
@login_required
def update_status(sample_id):
    """Update the status for a sample."""
    sample_obj = sample_or_404(sample_id)
    new_status = request.form['status'] or None
    comment_update = request.form['comment']
    sample_obj.update_status(new_status, comment_update)
    db.commit()
    return redirect(url_for('.sample', sample_id=sample_id))


@genotype_bp.route('/samples')
@login_required
def samples():
    """Search for a sample in the database."""
    sample_q = Sample.query
    plate_id = request.args.get('plate')
    if plate_id:
        plate_pattern = "%/{}\_%".format(plate_id)
        sample_q = (sample_q.join(Sample.analyses)
                            .filter(Analysis.source.like(plate_pattern)))

    if 'incomplete' in request.args:
        sample_q = api.incomplete(query=sample_q)
    if 'commented' in request.args:
        sample_q = sample_q.filter(Sample.comment != None)

    # search samples
    query_str = request.args.get('query')
    if query_str:
        sample_q = sample_q.filter(Sample.id.like("%{}%".format(query_str)))

    sample_count = sample_q.count()
    if sample_count == 1:
        # I'm feeling lucky
        sample_obj = sample_q.first()
        return redirect(url_for('.sample', sample_id=sample_obj.id))
    elif sample_count == 0:
        flash("no samples matching the query: {}".format(query_str))

    req_args = request.args.to_dict()
    if 'page' in req_args:
        del req_args['page']
    per_page = 100 if 'show_more' in request.args else 30
    page = int(request.args.get('page', 1))
    page = sample_q.paginate(page, per_page=per_page)
    return render_template('genotype/samples.html', samples=page,
                           req_args=req_args, plates=api.plates())


@genotype_bp.route('/samples/<sample_id>/delete', methods=['POST'])
@login_required
def delete_sample(sample_id):
    """Delete a whole sample from the database."""
    sample_obj = sample_or_404(sample_id)
    sample_obj.delete()
    flash("delete sample: {}".format(sample_obj.id), 'info')
    db.commit()
    return redirect(url_for('.dashboard'))


def sample_or_404(sample_id):
    """Fetch sample or redirect user to 404 page."""
    sample_obj = api.sample(sample_id)
    if sample_obj is None:
        return abort(404, "sample not found: {}".format(sample_id))
    return sample_obj


@genotype_bp.route('/samples/missing/<data>')
@login_required
def missing(data):
    """Samples with missing information to be compared."""
    query = (api.missing_sex() if data == 'sex' else
             api.missing_genotypes(db.session, data))

    per_page = 30
    page_no = int(request.args.get('page', 1))
    page = query.paginate(page_no, per_page=per_page)
    return render_template('genotype/missing.html', samples=page, missing=data)


@genotype_bp.route('/plates')
@login_required
def plates():
    """List all added plates with status."""
    plate_query = api.plates()
    return render_template('genotype/plates.html', plates=plate_query)


@genotype_bp.route('/plates/<plate_id>')
@login_required
def plate(plate_id):
    """Provide details about a plate and option to sign off."""
    plate_obj = api.plate(plate_id)
    return render_template('genotype/plate.html', plate=plate_obj)


@genotype_bp.route('/plates/<plate_id>/sign-off', methods=['POST'])
@login_required
def sign_off(plate_id):
    """Sign off on a plate that it's complete."""
    return redirect(request.referrer)
