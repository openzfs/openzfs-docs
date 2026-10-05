"""Regression tests for upstream descriptions and their RST representation."""

import io
import shutil

import pytest
from docutils.core import publish_doctree

from man_description import descriptions
import module_params


pytestmark = pytest.mark.skipif(not shutil.which('mandoc'), reason='mandoc required')


def validate_rst(text):
    warnings = io.StringIO()
    tree = publish_doctree(text, settings_overrides={'warning_stream': warnings})
    assert not warnings.getvalue(), warnings.getvalue()
    return tree.astext()


def test_mdoc_paragraphs_nested_lists_and_tables():
    source = '''.Dd October 5, 2026
.Dt ZFS 4
.Os
.Sh DESCRIPTION
.Bl -tag -width Ds
.It Sy l2arc_mfuonly Ns = Ns Sy 0 Ns | Ns 1 Ns | Ns 2 Pq int
Cache data and metadata.
.Pp
Setting it to 2 caches all metadata but only MFU data.
.Bl -tag -width Ds
.It Sy other_parameter
A nested term must not replace the real parameter description.
.El
.TS
tab(:);
l l.
Value:Meaning
2:MFU data
.TE
.It Sy other_parameter Ns = Ns Sy 0 Pq int
The real second parameter.
.Bd -literal
some_code();
.Ed
.El
.Sh SEE ALSO
.Xr zfs 4
'''
    result = descriptions(source, {'l2arc_mfuonly', 'other_parameter'})
    text = validate_rst(result['l2arc_mfuonly'])
    assert 'Setting it to 2' in text
    assert 'nested term' in text
    assert 'Value' in text and 'MFU data' in text
    assert 'The real second parameter' not in text
    assert 'nested term' not in result['other_parameter']
    assert 'some_code();' in validate_rst(result['other_parameter'])


def test_old_man_paragraphs_and_markup():
    source = r'''.TH ZFS-MODULE-PARAMETERS 5
.SH MODULE PARAMETERS
.TP
\fBexample_parameter\fR (int)
Literal *stars*, `backticks`, and a_name_ must remain text.
.sp
Default value: \fB0\fR.
.TP
\fBsecond_parameter\fR (int)
A different description.
'''
    result = descriptions(source, {'example_parameter', 'second_parameter'})
    text = validate_rst(result['example_parameter'])
    assert '*stars*' in text and '`backticks`' in text and 'a_name_' in text
    assert 'Default value: 0.' in text
    assert 'different description' not in text


def test_historical_openzfs_indented_man_entries():
    source = r'''.TH ZFS-MODULE-PARAMETERS 5
.SH DESCRIPTION
.SS Module parameters
.sp
.na
\fBexample_parameter\fR (ulong)
.ad
.RS 12n
An indented description.
.sp
Default value: \fB0\fR.
.RE
.sp
\fBsecond_parameter\fR (int)
.RS 12n
A different description.
.RE
'''
    result = descriptions(source, {'example_parameter', 'second_parameter'})
    text = validate_rst(result['example_parameter'])
    assert 'An indented description.' in text
    assert 'Default value: 0.' in text
    assert 'different description' not in text


def test_newest_version_without_man_description_uses_source(monkeypatch):
    monkeypatch.setattr(module_params, 'select_versions',
                        lambda repo: {'2.4': 'old', 'master': 'new'})
    monkeypatch.setattr(module_params, 'extract_params', lambda repo, tag: {
        'example': {'desc': 'Source ' + tag, 'type': 'int'}})
    monkeypatch.setattr(module_params, 'parse_man', lambda repo, tag: {
        'example': {'man_desc': 'Old description'}} if tag == 'old' else {})
    params, _ = module_params.collect(None)
    assert 'man_desc' not in params['example']
    assert params['example']['desc'] == 'Source new'
