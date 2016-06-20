# -*- coding: utf-8 -*-
import logging
import os

from flask import (abort, Blueprint, current_app, flash, redirect,
                   render_template, request, url_for)
from werkzeug import secure_filename

from taboo.match.core import check_sample
from taboo.load.excel import load_excel
from taboo.store.models import Sample


logger = logging.getLogger(__name__)
genotype_bp = Blueprint('genotype', __name__, template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/genotype')


@genotype_bp.route('/')
def index():
    """Display all samples."""
    pending = current_app.config['TABOO_DB'].pending()
    failing = current_app.config['TABOO_DB'].failing()
    return render_template('genotype/index.html', pending=pending,
                           failing=failing)


@genotype_bp.route('/samples/<sample_id>')
def sample(sample_id):
    """Display information about a sample."""
    sample_obj = sample_or_404(sample_id)
    return render_template('genotype/sample.html', sample=sample_obj)


@genotype_bp.route('/upload', methods=['POST'])
def upload():
    """Upload an Excel report file from MAF."""
    db = current_app.config['TABOO_DB']
    include_key = current_app.config['TABOO_INCLUDE_KEY']

    req_file = request.files['excel']
    filename = secure_filename(req_file.filename)

    if not req_file or not filename.endswith('.xlsx'):
        return abort(500, 'Please select an Excel book for upload')

    excel_path = os.path.join(current_app.config['TABOO_GENOTYPE_DIR'], filename)
    req_file.save(excel_path)

    analyses = load_excel(excel_path, include_key=include_key)
    for analysis in analyses:
        loaded_analysis = db.add_analysis(analysis, replace=True)
        if loaded_analysis:
            flash("added: {}".format(analysis.sample.id), 'info')

    return redirect(url_for('.index'))


@genotype_bp.route('/check', methods=['POST'])
@genotype_bp.route('/check/<sample_id>', methods=['POST'])
def check(sample_id=None):
    """Check samples."""
    if sample_id:
        samples = [sample_or_404(sample_id)]
        url = url_for('.sample', sample_id=sample_id)
    else:
        # fetch all pending samples
        samples = current_app.config['TABOO_DB'].pending()
        url = url_for('.index')

    for sample in samples:
        cutoffs = dict(max_nocalls=current_app.config['TABOO_MAX_NOCALLS'],
                       max_mismatch=current_app.config['TABOO_MAX_MISMATCH'],
                       min_matches=current_app.config['TABOO_MIN_MATCHES'],)
        results = check_sample(sample, **cutoffs)
        sample.status = 'fail' if 'fail' in results.values() else 'pass'
    current_app.config['TABOO_DB'].save()
    return redirect(url)


@genotype_bp.route('/update/<sample_id>', methods=['POST'])
def update(sample_id):
    """Update information about a sample."""
    sample_obj = sample_or_404(sample_id)
    sample_obj.sex = request.form['sample_sex'] or None
    sample_obj.comment = request.form['comment']
    for analysis in sample_obj.analyses:
        analysis.sex = request.form["{}_sex".format(analysis.type)] or None
    current_app.config['TABOO_DB'].save()
    return redirect(url_for('.sample', sample_id=sample_id))


@genotype_bp.route('/update-status/<sample_id>', methods=['POST'])
def update_status(sample_id):
    """Update the status for a sample."""
    sample_obj = sample_or_404(sample_id)
    new_status = request.form['status'] or None
    comment_update = request.form['comment']
    sample_obj.update_status(new_status, comment_update)
    current_app.config['TABOO_DB'].save()
    return redirect(url_for('.sample', sample_id=sample_id))


@genotype_bp.route('/samples/search')
def search_samples():
    """Search for a sample in the database."""
    query_str = request.args.get('query')
    query = Sample.query.filter(Sample.id.like("%{}%".format(query_str)))
    # I'm feeling lucky
    sample_obj = query.first()

    if sample_obj:
        return redirect(url_for('.sample', sample_id=sample_obj.id))
    else:
        flash("no samples matching the query: {}".format(query_str))
        return redirect(url_for('.index'))


def sample_or_404(sample_id):
    """Fetch sample or redirect user to 404 page."""
    sample_obj = Sample.query.get(sample_id)
    if sample_obj is None:
        return abort(404, "sample not found: {}".format(sample_id))
    return sample_obj
