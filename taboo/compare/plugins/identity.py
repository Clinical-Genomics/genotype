# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from toolz import pipe, unique
from toolz.curried import map

# class OutOfSyncError(StandardError):
#   """"""
#   pass


def site_id(site, delimiter='|'):
  """Build a unique ID for a specific variant position."""
  return delimiter.join(map(str, [site.CHROM, site.POS, site.REF, site.ALT[0]]))


def get_variant_id(sample, delimiter='|'):
  """Extract a guaranteed unique ID from a Call instance.

  Args:
    sample (:class:`vcf.model._Call`): sample Call instance
    delimiter (str, optional): string to use in alternative id

  Return:
    str: RS-number or unique combination of CHROM, POS, REF, and ALT
  """
  return (sample.site.ID or site_id(sample.site, delimiter=delimiter))


def identity(samples):
  """Return unique identifier for the given variant.

  Will raise an error is the samples belong to multitple variants.

  Args:
    samples (list of :class:`vcf.model._Call` instances): one variant

  Returns:
    list: all unique variant ids (should be only one)
  """
  identifiers = pipe(
    samples,
    map(get_variant_id),  # get unique variant ids
    unique,               # merge identical ids
    list                  # unwind them (usually *it*)
  )

  # if len(identifiers) > 1:
  #   raise OutOfSyncError(
  #     "Multiple IDs for the same position: %s" % ','.join(identifiers))

  # else:
  #   return identifiers[0]

  # normally returns just a single identifier, but just in case
  return identifiers
