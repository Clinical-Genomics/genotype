# -*- coding: utf-8 -*-
import codecs
import os

from flask import Flask, render_template, redirect, request, url_for, abort
from werkzeug import secure_filename

from taboo import rsnumbers
from taboo.input import load_excel
from taboo.match import fill_forward, run_comparison
from taboo.utils import unique_rsnumbers

app = Flask(__name__)


@app.route('/')
def index():
    """Display all samples."""
    plates = [plate_id.lstrip('/') for plate_id
              in app.config['store'].experiments('genotyping')]

    samples = (sample for sample in app.config['store'].samples()
               if sample.is_analyzed() and not sample.is_success())

    return render_template('index.html', plates=plates, samples=samples)


@app.route('/plates/<path:plate_id>')
def plate(plate_id):
    """Display all samples in a plate."""
    analyses = app.config['store'].analyses(source="/{}".format(plate_id))
    samples = (analysis.sample for analysis in analyses)
    return render_template('plate.html', samples=samples, plate_id=plate_id)


@app.route('/samples/<sample_id>')
def sample(sample_id):
    """Display details for a sample."""
    store = app.config['store']
    sample_obj = store.sample(sample_id)

    with codecs.open(app.config['rsnumber_ref'], 'r') as ref_handle:
        reference_dict = rsnumbers.parse(ref_handle)

    all_rsnumbers = unique_rsnumbers(store.session.query)
    experiments = {
        analysis.experiment: fill_forward(all_rsnumbers, reference_dict,
                                          analysis.genotypes)
        for analysis in sample_obj.analyses
    }
    genotype_pairs = zip(all_rsnumbers, *experiments.values())

    return render_template('sample.html', sample=sample_obj,
                           experiments=experiments, rsnumbers=all_rsnumbers,
                           genotype_pairs=genotype_pairs)


@app.route('/plates/analyze/<path:plate_id>')
def analyze_plate(plate_id):
    """Analyze all relevant samples on a plate."""
    store = app.config['store']
    plate_id = "/{}".format(plate_id)
    analyses = store.analyses(source=plate_id)
    relevant_analyses = (analysis for analysis in analyses
                         if len(analysis.sample.analyses) == 2)

    with codecs.open(app.config['rsnumber_ref'], 'r') as rs_stream:
        rs_lines = [line for line in rs_stream]

    for analysis in relevant_analyses:
        run_comparison(store, rs_lines, analysis.sample.sample_id)

    return redirect(url_for('plate', plate_id=plate_id.lstrip('/')))


@app.route('/analysis/<sample_id>')
def analysis(sample_id):
    store = app.config['store']
    with codecs.open(app.config['rsnumber_ref'], 'r') as rs_stream:
        run_comparison(store, rs_stream, sample_id)

    return redirect(request.referrer)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload an Excel report file from MAF."""
    db = app.config['store']
    include_key = '-CG-'

    req_file = request.files['excel_input']
    filename = secure_filename(req_file.filename)

    if not req_file or not filename.endswith('.xlsx'):
        return abort(500, 'Please select an Excel file for upload')

    excel_path = os.path.join(app.config['genotyping_dir'], filename)
    req_file.save(excel_path)

    analyses = load_excel(db, excel_path, include_key=include_key)
    for analysis in analyses:
        app.logger.info("added analysis: %s", analysis.sample.sample_id)

    return redirect(url_for('index'))
