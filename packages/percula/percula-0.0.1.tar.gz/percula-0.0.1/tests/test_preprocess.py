"""Unit tests for the preprocess module in the percula package."""
import json
from pathlib import Path

import pysam

from percula import preprocess

f1 = preprocess.adapters['adapter1_f']
f2 = preprocess.adapters['adapter2_f']
r1 = preprocess.adapters['adapter1_r']
r2 = preprocess.adapters['adapter2_r']

segment = 'AGCT' * 50  # Dummy read segment of 200 nt

reads = [
    {
        # 1 F segment
        'id': 'read1',
        'seq': f"AGCT{f1}{segment}{f2}",
        'segments': [['adapter1_f', 'adapter2_f']],
        'configs': {'subreads': 1, 'full_length': 1, 'stranded': 1, 'plus': 1},
    },
    {
        # 1 R segment
        'id': 'read2',
        'seq': f"AGCT{r2}{segment}{r1}",
        'segments': [['adapter2_r', 'adapter1_r']],
        'configs': {'subreads': 1, 'full_length': 1, 'stranded': 1, 'minus': 1},
    },
    {
        # 2 F segments
        'id': 'read3',
        'seq': f"AGCT{f1}{segment}{f2}{f1}{segment}{f2}AGCT",
        'segments': [
            ['adapter1_f', 'adapter2_f'],
            ['adapter1_f', 'adapter2_f']],
        'configs': {'subreads': 2, 'full_length': 1, 'stranded': 2, 'plus': 2},
    },
    {
        # 2 R segments
        'id': 'read4',
        'seq': f"AGCT{r2}{segment}{r1}{r2}{segment}{r1}AGCT",
        'segments': [
            ['adapter2_r', 'adapter1_r'],
            ['adapter2_r', 'adapter1_r']],
        'configs': {'subreads': 2, 'full_length': 1, 'stranded': 2, 'minus': 2},

    },
    {
        # 1 F and 1 R segment
        'id': 'read5',
        'seq': f"AGCT{f1}{segment}{f2}{r2}{segment}{r1}AGCT",
        'segments': [
            ['adapter1_f', 'adapter2_f'],
            ['adapter2_r', 'adapter1_r']],
        'configs': {
            'subreads': 2, 'full_length': 1, 'stranded': 2, 'plus': 1, 'minus': 1},
    },
    {
        # 1 F and 1 R segment, with singlet flanking adapters
        # which should not form part of a segment
        'id': 'read6',
        'seq': f"AGCT{r1}AGCT{f1}{segment}{f2}{r2}{segment}{r1}AGCT{f1}AGCT",
        'segments': [
            ['adapter1_f', 'adapter2_f'],
            ['adapter2_r', 'adapter1_r']],
        'configs': {
            'subreads': 2, 'full_length': 1, 'stranded': 2, 'plus': 1, 'minus': 1},
    },
    {
        # No adapters. No hosts returned.
        'id': 'read7',
        'seq': f"AGCT{segment}AGCT",
        'segments': [],
        'configs': {'no_adapters': 1, 'subreads': 0}
    }
]


def test_get_subreads():
    """Test the get_subreads function."""
    for r in reads:
        read = preprocess.Read(r['id'], r['seq'], '?' * len(r['seq']), None)
        # use a non-default r1/r2 size so everything passes through
        _, _, configs_summ, hit_summary = preprocess.get_subreads(
            read, r1_size=10, r2_size=10, min_id=0.8)
        summ = [x.split('\t') for x in hit_summary]
        assert len(summ) == len(r['segments'])

        assert dict(configs_summ) == r['configs']

        for seg, hit_sum in zip(r['segments'], summ):
            assert seg[0] == hit_sum[2]
            assert seg[1] == hit_sum[4]


def test_orient_reads():
    """Test the parent read and short reads contain correct content."""
    r1 = "CAT" * 20
    r2p = "TAG" * 20
    insert = f"{r1}{r2p}"

    read = f"GGGG{f1}{insert}{f2}TTTT"
    fwd_read = preprocess.Read(
        "fwd", read, "?" * len(read), None)
    # make also an r2-r1 read directly from the above
    rev_read = preprocess.Read(
        "rev", preprocess.reverse_complement(read), "?" * len(read), None)

    # run function for both variants
    fwd_pairs, fwd_parents, cs, hs = preprocess.get_subreads(
        fwd_read, r1_size=30, r2_size=30, min_id=0.8, min_length=0, trim=None)
    rev_pairs, rev_parents, _, _ = preprocess.get_subreads(
        rev_read, r1_size=30, r2_size=30, min_id=0.8, min_length=0, trim=None)

    # results should be equal (it doesn't matter which strand was sequenced)
    # this is a "f" read, which actually means anti-sense, and we want to
    # output the parent as the sense strand
    assert fwd_parents[0][1] == rev_parents[0][1]
    assert fwd_parents[0][1] == preprocess.reverse_complement(insert)

    # for the fwd read:
    #   after rotating to sense, r1 ended up at the end of the read, its
    #   then read outside in, which in effect means r1 is reverse complemented
    #   twice and so the same as the original in `read` that we constructed.
    #   r2 is reverse complemented once, due to the read being anti-sense.
    # and again, whether we sequenced the fwd or rev read, the result should
    # be the same.
    fwd_pair = tuple(fwd_pairs[0][i].splitlines()[1] for i in range(2))
    rev_pair = tuple(rev_pairs[0][i].splitlines()[1] for i in range(2))

    assert rev_pair == fwd_pair
    assert fwd_pair[0] == "CAT" * 10  # r1
    assert fwd_pair[1] == preprocess.reverse_complement("TAG") * 10  # r2


def test_entrypoint(tmp_path):
    """Test the command line entrypoint."""
    parser = preprocess.argument_parser()
    output_dir = tmp_path / "output"
    input_file = Path(__file__).parent / "data" / "reads.bam"
    args = parser.parse_args([
        str(output_dir), str(input_file), "--chunk_size", "250", "--threads", "1"])
    preprocess.main(args)


def test_outputs(tmpdir):
    """Test the output files are as expected."""
    parser = preprocess.argument_parser()
    output_dir = tmpdir / "output"
    input_dir = Path(__file__).parent / "data" / "output_test"
    args = parser.parse_args([
        str(output_dir), str(input_dir / "parents.bam"),
        "--chunk_size", "250", "--threads", "4"])
    preprocess.main(args)

    # Check the output files
    r1_out = output_dir / "SAMPLE_S1_L001_R1_001.fastq.gz"
    r1_expected = input_dir / "R1.fq.gz"

    with (
        pysam.FastxFile(r1_out) as fh_r1_out,
            pysam.FastxFile(r1_expected) as fh_r1_exp):

        for read_out, exp_read in zip(fh_r1_out, fh_r1_exp):
            assert read_out.name == exp_read.name
            assert read_out.sequence == exp_read.sequence
            assert read_out.quality == exp_read.quality

    r2_out = output_dir / "SAMPLE_S1_L001_R2_001.fastq.gz"
    r2_expected = input_dir / "R2.fq.gz"

    with (
        pysam.FastxFile(r2_out) as fh_r2_out,
            pysam.FastxFile(r2_expected) as fh_r2_exp):

        for read_out, exp_read in zip(fh_r2_out, fh_r2_exp):
            assert read_out.name == exp_read.name
            assert read_out.sequence == exp_read.sequence
            assert read_out.quality == exp_read.quality

    bam_out = output_dir / "SAMPLE_S1_L001.bam"
    bam_expected = input_dir / "trimmed.bam"

    with (
        pysam.AlignmentFile(bam_out, check_sq=False) as fh_bam,
            pysam.AlignmentFile(bam_expected, check_sq=False) as fh_bam_exp):
        for read_out, exp_read in zip(
                fh_bam.fetch(until_eof=True), fh_bam_exp.fetch(until_eof=True)):
            assert read_out.query_name == exp_read.query_name
            assert read_out.query_sequence == exp_read.query_sequence
            assert read_out.query_qualities == exp_read.query_qualities

    # Tesrt the final config summary that is populated with all possible values
    with open(output_dir / "configs.json", 'r') as cfg_fh:
        config_summ = json.load(cfg_fh)
        assert config_summ == {
            "single_adapter1": 0,
            "single_adapter2": 0,
            "double_adapter1": 0,
            "double_adapter2": 0,
            "no_adapters": 0,
            "full_length": 2,
            "subreads": 2,
            "stranded": 2,
            "plus": 1,
            "minus": 1,
            "other": 0
        }
