"""Tests for explicit value enumerations in upstream parameter headings."""

import pytest

import module_params


@pytest.mark.parametrize('heading,expected', [
    ('Ns = Ns Sy 0 Ns | Ns 1 Ns | Ns 2 Pq int', ('0', '1', '2')),
    ('Ns = Ns Sy 1 Ns | Ns 0 Pq uint', ('1', '0')),
    ('Ns = Ns 0 Ns | Ns 1 Pq int', ('0', '1')),
    ('Ns = Ns Sy -1 Ns | Ns 0 Ns | Ns 0x10 Pq int', ('-1', '0', '0x10')),
    ('Ns = Ns Sy 0 Pq int', ()),
    ('Ns = Ns Sy 33 Ns % Pq uint', ()),
    ('Ns = Ns Sy 0 Ns | Ns 1 Ns | Ns ... Pq int', ()),
    ('Ns = Ns Sy 0 Ns | Ns 1 Ns B Pq uint', ()),
])
def test_parse_explicit_alternatives(monkeypatch, heading, expected):
    source = '.It Sy example ' + heading + '\nExample description.\n'
    monkeypatch.setattr(module_params, 'read', lambda repo, tag, path:
                        source if path == 'man/man4/zfs.4' else '')
    monkeypatch.setattr(module_params, 'descriptions', lambda source, names: {})
    result = module_params.parse_man(None, 'master')['example']
    assert result.get('man_values', ()) == expected


def test_curated_range_overrides_upstream_values():
    values = ('0', '1', '2')
    assert module_params.range_field('', values) == r'``0`` \| ``1`` \| ``2``'
    assert module_params.range_field('0 to 1', values) == '0 to 1'
    table = module_params.range_field('0=off, 1=on', values)
    assert '   * - ``0``' in table
    assert '   * - ``1``' in table
    assert '   * - ``2``' not in table


def test_newer_version_does_not_inherit_old_enumeration(monkeypatch):
    monkeypatch.setattr(module_params, 'select_versions',
                        lambda repo: {'2.4': 'old', 'master': 'new'})
    monkeypatch.setattr(module_params, 'extract_params', lambda repo, tag: {
        'example': {'desc': 'Source ' + tag, 'type': 'int'}})
    monkeypatch.setattr(module_params, 'parse_man', lambda repo, tag: {
        'example': {'man_values': ('0', '1')}} if tag == 'old' else {})
    params, _ = module_params.collect(None)
    assert 'man_values' not in params['example']
