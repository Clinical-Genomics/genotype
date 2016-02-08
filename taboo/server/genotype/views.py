# -*- coding: utf-8 -*-
import codecs
import logging
import os

from flask import (Blueprint, current_app, render_template, redirect,
                   request, url_for, abort)
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import secure_filename

from taboo import rsnumbers
from taboo.input import load_excel
from taboo.match import fill_forward, run_comparison
from taboo.utils import unique_rsnumbers


logger = logging.getLogger(__name__)
genotype_bp = Blueprint('genotype', __name__, template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/genotype')


@genotype_bp.route('/')
def index():
    """Display all samples."""
    plates = [(os.path.basename(plate_id), plate_id.lstrip('/')) for plate_id
              in current_app.config['store'].experiments('genotyping')]

    return render_template('genotype/index.html', plates=plates)


@genotype_bp.route('/plates/<path:plate_id>')
def plate(plate_id):
    """Display all samples in a plate."""
    analyses = current_app.config['store'].analyses(source="/{}".format(plate_id))
    samples = (analysis.sample for analysis in analyses)
    return render_template('genotype/plate.html', samples=samples,
                           plate_id=plate_id)


@genotype_bp.route('/plates/delete', methods=['POST'])
def delete_plate():
    """Delete Analysis and Related result models."""
    plate_id = "/{}".format(request.form['plate_id'])
    current_app.config['store'].remove_analysis(plate_id)
    return redirect(url_for('.index'))


@genotype_bp.route('/samples/<sample_id>')
def sample(sample_id):
    """Display details for a sample."""
    store = current_app.config['store']
    sample_obj = store.sample(sample_id)

    with codecs.open(current_app.config['rsnumber_ref'], 'r') as ref_handle:
        reference_dict = rsnumbers.parse(ref_handle)

    all_rsnumbers = unique_rsnumbers(store.session.query)

    analyses = [sample_obj.analysis_dict['genotyping'],
                sample_obj.analysis_dict['sequencing']]
    experiments = [fill_forward(all_rsnumbers, reference_dict,
                                analysis.genotypes)
                   for analysis in analyses]
    genotype_pairs = zip(all_rsnumbers, *experiments)

    return render_template('genotype/sample.html', sample=sample_obj,
                           rsnumbers=all_rsnumbers,
                           genotype_pairs=genotype_pairs)


@genotype_bp.route('/samples/<sample1>/<sample2>')
def compare_samples(sample1, sample2):
    """Compare genotypes between samples.

    Genotyping results will be used for 'sample1', and sequencing results
    will be used for 'sample2'.
    """
    store = current_app.config['store']
    sample_1 = store.sample(sample1)
    sample_2 = store.sample(sample2)

    genotyping = sample_1.analysis_dict['genotyping']
    sequencing = sample_2.analysis_dict['sequencing']

    with codecs.open(current_app.config['rsnumber_ref'], 'r') as ref_handle:
        reference_dict = rsnumbers.parse(ref_handle)

    all_rsnumbers = unique_rsnumbers(store.session.query)
    experiments = [fill_forward(all_rsnumbers, reference_dict,
                                analysis.genotypes)
                   for analysis in [genotyping, sequencing]]
    genotype_pairs = zip(all_rsnumbers, *experiments)

    return render_template('genotype/compare.html', sample1=sample_1,
                           sample2=sample_2, rsnumbers=all_rsnumbers,
                           genotype_pairs=genotype_pairs)


@genotype_bp.route('/plates/analyze/<path:plate_id>')
def analyze_plate(plate_id):
    """Analyze all relevant samples on a plate."""
    store = current_app.config['store']
    plate_id = "/{}".format(plate_id)
    analyses = store.analyses(source=plate_id)
    relevant_analyses = (analysis for analysis in analyses
                         if len(analysis.sample.analyses) == 2)

    with codecs.open(current_app.config['rsnumber_ref'], 'r') as rs_stream:
        rs_lines = [line for line in rs_stream]

    for analysis in relevant_analyses:
        run_comparison(store, rs_lines, analysis.sample.sample_id)

    return redirect(url_for('.plate', plate_id=plate_id.lstrip('/')))


@genotype_bp.route('/analysis/<sample_id>')
def analysis(sample_id):
    store = current_app.config['store']
    with codecs.open(current_app.config['rsnumber_ref'], 'r') as rs_stream:
        run_comparison(store, rs_stream, sample_id)

    return redirect(request.referrer)


@genotype_bp.route('/upload', methods=['POST'])
def upload():
    """Upload an Excel report file from MAF."""
    db = current_app.config['store']
    include_key = '-CG-'

    req_file = request.files['excel_input']
    filename = secure_filename(req_file.filename)

    if not req_file or not filename.endswith('.xlsx'):
        return abort(500, 'Please select an Excel file for upload')

    excel_path = os.path.join(current_app.config['genotyping_dir'], filename)
    req_file.save(excel_path)

    analyses = load_excel(db, excel_path, include_key=include_key)
    for analysis in analyses:
        current_app.logger.info("added analysis: %s", analysis.sample.sample_id)

    return redirect(url_for('.index'))


@genotype_bp.route('/search')
def search_sample():
    """Find a plate using a sample id."""
    sample_id = request.args.get('sample_id')
    try:
        sample_obj = current_app.config['store'].sample(sample_id)
    except NoResultFound:
        return abort(404, "no sample found: {}".format(sample_id))
    analysis_obj = sample_obj.analysis_dict.get('genotyping')
    if analysis_obj is None:
        return abort(404, "no genotyping results loaded: {}".format(sample_id))
    return redirect(url_for('.plate', plate_id=analysis_obj.source.lstrip('/')))
