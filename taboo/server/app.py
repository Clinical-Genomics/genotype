# -*- coding: utf-8 -*-
import codecs

from flask import Flask, render_template, request

from taboo.match import match_sample, sort_scores, compare_sample

app = Flask(__name__)


@app.route('/')
def index():
    """Display all samples."""
    samples = app.config['store'].samples().order_by('sample_id')
    return render_template('index.html', samples=samples)


@app.route('/analysis/<sample_id>/<experiment>')
def analysis(sample_id, experiment):
    limit = int(request.args.get('limit', 10))

    store = app.config['store']
    alt_experiment = 'sequencing' if experiment == 'genotyping' else 'genotyping'
    with codecs.open(app.config['rsnumber_ref'], 'r') as rs_stream:
        comparisons = match_sample(store, rs_stream, sample_id,
                                   experiment, alt_experiment)
        ranked_comparisons = sort_scores(comparisons)

    is_success = compare_sample(ranked_comparisons, sample_id)
    comparisons = ranked_comparisons[:limit]
    return render_template('analysis.html', comparisons=comparisons,
                           is_success=is_success, sample_id=sample_id)
