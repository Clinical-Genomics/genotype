# -*- coding: utf-8 -*-
import codecs
import os

from flask import Flask, render_template, redirect, request, url_for, abort
from sqlalchemy import desc
from werkzeug import secure_filename

from taboo.input import load_excel
from taboo.match import run_comparison

app = Flask(__name__)


@app.route('/')
def index():
    """Display all samples."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 30))
    samples = (app.config['store'].samples().order_by(desc('created_at'))
                                            .offset(skip)
                                            .limit(limit))
    return render_template('index.html', samples=samples, skip=skip, limit=limit)


@app.route('/analysis/<sample_id>')
def analysis(sample_id):
    limit = request.args.get('limit', 10)
    skip = request.args.get('skip', 10)

    experiment = request.args.get('experiment', 'genotyping')
    store = app.config['store']
    alt_experiment = 'sequencing' if experiment == 'genotyping' else 'genotyping'
    with codecs.open(app.config['rsnumber_ref'], 'r') as rs_stream:

        run_comparison(store, rs_stream, sample_id, experiment, alt_experiment)

    return redirect(url_for('index', skip=skip, limit=limit))


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
