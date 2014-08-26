# -*- coding: utf-8 -*-


def test_pipeline():
  ref = [
    '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE\tID-000026T',
    '14\t55817708\trs10144418\tT\tC\t.\t.\t.\tGT\t0/1',
    '17\t71197748\trs1037256\tG\tA\t.\t.\t.\tGT\t0/0',
    '2\t85553784\trs1044973\tC\tT\t.\t.\t.\tGT\t0/1'
  ]

  alt = [
    '##fileformat=VCFv4.2',
    '##FILTER=<ID=LowQual,Description="Low quality">',
    '##FILTER=<ID=VQSRTrancheBOTH99.90to100.00+,Description="Truth">',
    '#CHROM POS ID  REF ALT QUAL  FILTER  INFO  FORMAT  118-1-2A',
    '14\t55817708\trs10144418\tT\tC\t116423.73\tPASS\tAC=7;AF=0.667;\tGT\t0/1'
  ]
