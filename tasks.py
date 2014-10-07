#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from invoke import run, task
from invoke.util import log


@task
def test():
  """test - run the test runner."""
  run('python setup.py test', pty=True)


@task(name='test-all')
def testall():
  """test-all - run tests on every Python version with tox."""
  run('tox')


@task
def clean():
  """clean - remove build artifacts."""
  run('rm -rf build/')
  run('rm -rf dist/')
  run('rm -rf taboo.egg-info')
  run('find . -name __pycache__ -delete')
  run('find . -name *.pyc -delete')
  run('find . -name *.pyo -delete')
  run('find . -name *~ -delete')

  log.info('cleaned up')


@task
def lint():
  """lint - check style with flake8."""
  run('flake8 taboo tests')


@task
def coverage():
  """coverage - check code coverage quickly with the default Python."""
  run('coverage run --source taboo setup.py test')
  run('coverage report -m')
  run('coverage html')
  run('open htmlcov/index.html')

  log.info('collected test coverage stats')


@task(clean)
def publish(test=False):
  """publish - package and upload a release to the cheeseshop."""
  if test:
    run('python setup.py register -r test sdist upload -r test')
  else:
    run('python setup.py register bdist_wheel upload')
    run('python setup.py register sdist upload')

  log.info('published new release')
