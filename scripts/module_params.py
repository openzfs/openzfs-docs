#!/usr/bin/env python3
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# License: CC0 https://creativecommons.org/share-your-work/public-domain/cc0/
#
# Generate the "Module Parameters" page from the OpenZFS sources.
#
# The list of parameters, their types, permissions, defaults and one-line
# descriptions are taken from the OpenZFS git repository: the
# ZFS_MODULE_PARAM* macros for the "zfs" module, plain module_param() for
# the Linux SPL module, and man/man4/zfs.4 for the defaults.  Every
# release branch is parsed, so each parameter also carries the list of
# versions it exists in.
#
# Everything that cannot be derived from the sources - tags, tuning
# advice, how to verify a setting took effect - lives in the overlay file
# (see OVERLAY_NAME) and is maintained by hand.  An overlay entry for a
# parameter that no longer exists anywhere is an error: that is what
# keeps this page from drifting away from reality again.

import argparse
import logging
import os
import re
import sys
from collections import defaultdict

import git
import yaml

LOG = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

BUILD_DIR = '_build'
ZFS_GIT_REPO = 'https://github.com/openzfs/zfs.git'
ZFS_GIT_DIR = os.path.join(BUILD_DIR, 'zfs')

DOCS_REPO_URL = 'https://github.com/openzfs/openzfs-docs/'
OVERLAY_NAME = 'module_parameters.yaml'
PAGE_PATH = os.path.join('Performance and Tuning', 'Module Parameters.rst')
INTRO_NAME = '_module_parameters_intro.rst'

TAG_REGEX = re.compile(
    r'zfs-(?P<version>(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<fix>[0-9]+))$')

# ZFS_MODULE_PARAM(scope, name_prefix, name, type, perm, desc)
# ZFS_MODULE_PARAM_CALL(scope, name_prefix, name, set, get, perm, desc)
PARAM_MACRO = re.compile(
    r'\bZFS_MODULE_PARAM(?P<call>_CALL(?:_IMPL)?)?\s*\((?P<args>.*?)\)\s*;',
    re.DOTALL)
# Before OpenZFS 2.0 parameters were declared with the plain Linux macros;
# the SPL ones still are.
LEGACY_MACRO = re.compile(
    r'^module_param(?:_named|_call|_array)?\((?P<args>.*?)\)\s*;',
    re.DOTALL | re.MULTILINE)
LEGACY_DESC = re.compile(
    r'\bMODULE_PARM_DESC\(\s*(?P<name>[a-z][a-z0-9_]*)\s*,\s*(?P<desc>.*?)\)'
    r'\s*;', re.DOTALL)
# .It Sy zfs_arc_min Ns = Ns Sy 0 Ns B Pq u64
MAN_ENTRY = re.compile(r'^\.It Sy (?P<name>[a-z][a-z0-9_]*)\b(?P<rest>.*)$')

PERM_LABEL = {
    'ZMOD_RW': 'Dynamic',
    'ZMOD_RD': 'Prior to module load',
}


def split_args(text):
    """Split macro arguments on top-level commas, keeping strings intact."""
    args, depth, cur, in_string = [], 0, '', False
    i = 0
    while i < len(text):
        char = text[i]
        if in_string:
            if char == '\\':
                cur += text[i:i + 2]
                i += 2
                continue
            if char == '"':
                in_string = False
            cur += char
        elif char == '"':
            in_string = True
            cur += char
        elif char in '([':
            depth += 1
            cur += char
        elif char in ')]':
            depth -= 1
            cur += char
        elif char == ',' and depth == 0:
            args.append(cur.strip())
            cur = ''
        else:
            cur += char
        i += 1
    args.append(cur.strip())
    return args


def join_string_literals(args):
    """Concatenate the adjacent C string literals of the description."""
    literals = [a for a in args if a.startswith('"')]
    if not literals:
        return ''
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', literals[-1])
    return ''.join(parts).replace('\\"', '"').replace('\\n', ' ').strip()


def platform_of(path):
    if '/os/linux/' in path:
        return ['Linux']
    if '/os/freebsd/' in path:
        return ['FreeBSD']
    return ['Linux', 'FreeBSD']


def files_with(repo, tag, pattern, *pathspec):
    """List files matching a pattern in a tree, without checking it out."""
    try:
        out = repo.git.grep('-l', pattern, tag, '--', *pathspec)
    except git.exc.GitCommandError:
        return []
    return [line.split(':', 1)[1] for line in out.split('\n') if ':' in line]


def read(repo, tag, path):
    try:
        return repo.git.show('{}:{}'.format(tag, path))
    except git.exc.GitCommandError:
        return ''


def parse_man(repo, tag):
    """Defaults and units as documented in the man pages."""
    defaults = {}
    for man in ('man/man4/zfs.4', 'man/man4/spl.4'):
        for line in read(repo, tag, man).split('\n'):
            match = MAN_ENTRY.match(line)
            if not match:
                continue
            rest = match.group('rest')
            value = re.search(r'Ns = Ns Sy (?P<default>\S+)', rest)
            units = re.search(r'Ns (?P<units>[A-Za-z%]+) Ns', rest)
            kind = re.search(r'Pq (?P<type>[a-z][a-z0-9_]*)', rest)
            defaults[match.group('name')] = {
                'default': value.group('default') if value else '',
                'units': units.group('units') if units else '',
                'man_type': kind.group('type') if kind else '',
                'in_man': True,
            }
    return defaults


def extract_legacy(text, path):
    """Parameters declared with the plain Linux module_param macros."""
    params = {}
    descs = {m.group('name'): join_string_literals([m.group('desc')])
             for m in LEGACY_DESC.finditer(text)}
    for match in LEGACY_MACRO.finditer(text):
        args = split_args(match.group('args'))
        name = args[0].strip()
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            continue
        mode = next((a for a in reversed(args)
                     if re.match(r'^0[0-7]{3}$', a.strip())), '')
        params[name] = {
            'type': args[1].strip() if len(args) == 3 else '',
            'perm': 'ZMOD_RW' if mode.endswith(('6', '4')) and mode[1] in '67'
                    else 'ZMOD_RD',
            'desc': descs.get(name, ''),
            'platforms': platform_of(path),
        }
    return params


def extract_params(repo, tag):
    """All module parameters declared in a given tree."""
    params = {}
    for path in files_with(repo, tag, '^module_param', '*.c'):
        if not path.startswith('module/'):
            continue
        params.update(extract_legacy(read(repo, tag, path), path))
    for path in files_with(repo, tag, 'ZFS_MODULE_PARAM', '*.c'):
        # headers only define the macros, they declare no parameters
        if not path.startswith('module/'):
            continue
        text = read(repo, tag, path)
        for match in PARAM_MACRO.finditer(text):
            args = split_args(match.group('args'))
            if len(args) < 4:
                continue
            prefix = '' if args[1] in ('', '_') else args[1]
            name = (prefix + args[2]).strip()
            if not re.match(r'^[a-z][a-z0-9_]*$', name):
                continue  # the macro definition itself, not a parameter
            perm = next((a for a in args if a.startswith('ZMOD')), '')
            params[name] = {
                'type': '' if match.group('call') else args[3].lower(),
                'perm': perm,
                'desc': join_string_literals(args),
                'platforms': platform_of(path),
            }
    return params


def select_versions(repo):
    """Latest patch release of every minor version, plus master."""
    versions = {}
    for tag in sorted(repo.tags, key=lambda t: t.commit.committed_datetime):
        match = TAG_REGEX.match(str(tag))
        if not match:
            continue
        major, minor = int(match.group('major')), int(match.group('minor'))
        if major == 0 and minor < 6:
            continue
        versions['{}.{}'.format(major, minor)] = str(tag)
    versions['master'] = 'master'
    return versions


def collect(repo):
    """Merge the parameters of every version into one table."""
    versions = select_versions(repo)
    LOG.info('Versions to parse: %s', ', '.join(versions))

    per_version, mans = {}, {}
    for version, tag in versions.items():
        per_version[version] = extract_params(repo, tag)
        mans[version] = parse_man(repo, tag)
        LOG.info('%s (%s): %d parameters', version, tag,
                 len(per_version[version]))

    params = {}
    order = list(versions)
    for version in order:
        for name, meta in per_version[version].items():
            entry = params.setdefault(name, {'versions': []})
            entry['versions'].append(version)
            # newest version wins, so the page describes current behaviour
            entry.update(meta)
            entry.update(mans[version].get(name, {}))
    return params, order


def version_class(version):
    return 'v-' + version.replace('.', '-')


CODE_SPAN = re.compile(r'``[^`]*``')
# a trailing underscore turns the preceding word into a hyperlink reference
TRAILING_UNDERSCORE = re.compile(r'(?<=\w)_(?=\W|$)')


def rst_escape(text):
    """Escape inline markup in text taken from the sources, but not inside
    the ``literals`` of the curated overlay."""
    out, last = [], 0
    for span in CODE_SPAN.finditer(text):
        out.append(escape_plain(text[last:span.start()]))
        out.append(span.group(0))
        last = span.end()
    out.append(escape_plain(text[last:]))
    return ''.join(out)


def escape_plain(text):
    text = text.replace('*', r'\*').replace('|', r'\|')
    return TRAILING_UNDERSCORE.sub(r'\\_', text)


def version_range(present, order):
    """'0.8 - master' or '2.1, 2.3 - master' for parameters that came back."""
    index = {v: i for i, v in enumerate(order)}
    runs, start, prev = [], None, None
    for version in sorted(present, key=lambda v: index[v]):
        if start is None:
            start = prev = version
            continue
        if index[version] == index[prev] + 1:
            prev = version
            continue
        runs.append((start, prev))
        start = prev = version
    if start is not None:
        runs.append((start, prev))
    return ', '.join(a if a == b else '{} - {}'.format(a, b) for a, b in runs)


def render(params, order, overlay, intro_include):
    tags = defaultdict(list)
    for name, meta in params.items():
        for tag in overlay.get(name, {}).get('tags', []):
            tags[tag].append(name)

    out = [
        '.. THIS FILE IS AUTOGENERATED BY scripts/module_params.py,'
        ' DO NOT EDIT!',
        '..',
        '.. Curated content lives in docs/{}, the rest comes'.format(
            OVERLAY_NAME),
        '.. from the OpenZFS sources.',
        '',
        ':llms-txt-ignore: true',
        # the page itself is not in the repository, send "Edit on GitHub" to
        # the file a reader would actually want to change
        ':github_url: {}blob/master/docs/{}'.format(DOCS_REPO_URL,
                                                    OVERLAY_NAME),
        '',
        'Module Parameters',
        '=================',
        '',
        '.. raw:: html',
        '',
        '   <div id="zfs-param-filter"></div>',
        '',
        '.. include:: {}'.format(intro_include),
        '',
    ]

    if tags:
        out += ['Tags', '----', '',
                'The list of parameters is large and resists hierarchical',
                'representation. Each parameter is tagged with keywords for',
                'frequent searches.', '']
        for tag in sorted(tags, key=str.lower):
            out += ['.. rst-class:: zfs-tag', '',
                    tag, '~' * len(tag), '', '.. raw:: html', '', '   <ul>']
            for name in sorted(tags[tag]):
                classes = ' '.join(
                    ['zfs-param'] +
                    [version_class(v) for v in params[name]['versions']])
                out.append(
                    '   <li class="{cls}"><a href="#{anchor}">{name}</a>'
                    '</li>'.format(cls=classes, name=name,
                                   anchor=name.replace('_', '-')))
            out += ['   </ul>', '']

    out += ['Parameters', '----------', '']
    for name in sorted(params):
        meta = params[name]
        curated = overlay.get(name, {})
        classes = ['zfs-param'] + [version_class(v) for v in meta['versions']]
        out += [
            '.. rst-class:: ' + ' '.join(classes),
            '',
            name,
            '~' * len(name),
            '',
        ]
        fields = [
            ('Versions', version_range(meta['versions'], order)),
            ('Platforms', ', '.join(meta['platforms'])),
            ('Type', '``{}``'.format(meta['type'] or meta.get('man_type', ''))
             if (meta['type'] or meta.get('man_type')) else ''),
            ('Default', '``{}``'.format(meta['default'])
             if meta.get('default') else ''),
            ('Units', meta.get('units', '')),
            ('Range', curated.get('range', '')),
            ('Change', PERM_LABEL.get(meta['perm'], '')),
            ('Tags', ', '.join(curated.get('tags', []))),
        ]
        for label, value in fields:
            if value:
                out.append(':{}: {}'.format(label, value))
        out.append('')
        if meta['desc']:
            out += [rst_escape(meta['desc']), '']
        for label, key in (('When to change', 'when_to_change'),
                           ('Verification', 'verification'),
                           ('Notes', 'notes')):
            if curated.get(key):
                out += ['**{}:** {}'.format(label, rst_escape(curated[key])),
                        '']
    return '\n'.join(out) + '\n'


def coverage(params, overlay, order):
    """Parameters that exist in the code but are missing from the docs.

    "undocumented" ones have nothing at all: no description in the sources,
    no man page entry and no curated notes, so the page can only show their
    name. "uncurated" ones are described upstream but carry none of the
    advice this page exists for, grouped by the version that introduced
    them.
    """
    current = order[-1]
    undocumented, uncurated = [], defaultdict(list)
    for name, meta in sorted(params.items()):
        if current not in meta['versions']:
            continue  # removed upstream, nothing to document
        if name in overlay:
            continue
        if not meta['desc'] and not meta.get('in_man'):
            undocumented.append(name)
        else:
            uncurated[meta['versions'][0]].append(name)
    return undocumented, uncurated


def report_coverage(params, overlay, order, report_path=None):
    """Complain about undocumented parameters, loudly."""
    undocumented, uncurated = coverage(params, overlay, order)
    missing = sum(len(names) for names in uncurated.values())
    total = sum(1 for meta in params.values() if order[-1] in meta['versions'])

    for name in undocumented:
        LOG.error('%s exists in the sources but is documented nowhere: '
                  'no description upstream and no entry in %s',
                  name, OVERLAY_NAME)
    LOG.warning('%d of %d parameters have no curated notes in %s',
                missing, total, OVERLAY_NAME)
    for version in sorted(uncurated, key=lambda v: order.index(v),
                          reverse=True)[:2]:
        LOG.warning('  new in %s, still undocumented: %s',
                    version, ', '.join(uncurated[version]))

    if report_path:
        write_report(report_path, undocumented, uncurated, missing, total)
    return not undocumented


def write_report(path, undocumented, uncurated, missing, total):
    """Markdown summary, meant for $GITHUB_STEP_SUMMARY."""
    lines = ['## OpenZFS module parameter coverage', '',
             '{} of {} parameters have no curated notes in `{}`.'.format(
                 missing, total, OVERLAY_NAME), '']
    if undocumented:
        lines += ['### Documented nowhere', '',
                  'These have no upstream description either, so the page '
                  'can only show their name:', '']
        lines += ['- `{}`'.format(name) for name in undocumented] + ['']
    if uncurated:
        lines += ['### Missing tuning notes, by the version that added them',
                  '', '| Version | Count | Parameters |', '|---|---|---|']
        for version in sorted(uncurated, reverse=True):
            names = uncurated[version]
            lines.append('| {} | {} | {} |'.format(
                version, len(names),
                ' '.join('`{}`'.format(n) for n in names)))
        lines.append('')
    with open(path, 'a') as handle:
        handle.write('\n'.join(lines) + '\n')
    LOG.info('Wrote coverage report to %s', path)


def check_overlay(repo, params, overlay):
    """Fail on curated entries for parameters that never existed."""
    unknown = sorted(set(overlay) - set(params))
    if unknown:
        LOG.error('Overlay describes %d unknown parameters: %s',
                  len(unknown), ', '.join(unknown))

    # Identifiers mentioned in the curated text that are neither a parameter
    # nor anything else in the current sources are almost certainly leftovers
    # from a tunable that has been removed upstream.
    mentioned = defaultdict(set)
    for name, entry in overlay.items():
        text = ' '.join(str(v) for key, v in entry.items() if key != 'tags')
        for token in re.findall(r'\b[a-z][a-z0-9]*(?:_[a-z0-9]+){2,}\b', text):
            if token not in params and token != name:
                mentioned[token].add(name)
    for token in sorted(mentioned):
        if files_with(repo, 'master', r'\b{}\b'.format(token), '*.c', '*.h'):
            continue  # still exists in the sources, just not as a parameter
        LOG.warning('Overlay of %s mentions %s, which no longer exists',
                    ', '.join(sorted(mentioned[token])), token)
    return not unknown


def prepare_repo(out_dir):
    repo_dir = os.path.join(out_dir, BUILD_DIR)
    os.makedirs(repo_dir, exist_ok=True)
    try:
        repo = git.Repo(os.path.join(out_dir, ZFS_GIT_DIR))
        LOG.info('zfs repo already cloned')
        for remote in repo.remotes:
            remote.fetch(tags=None)
    except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError):
        LOG.info('Clone zfs repo...')
        git.Git(repo_dir).clone(ZFS_GIT_REPO)
        repo = git.Repo(os.path.join(out_dir, ZFS_GIT_DIR))
    return repo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out_dir', help='Sphinx docs dir')
    parser.add_argument('--check', action='store_true',
                        help='validate the overlay and the coverage of the '
                             'current parameters, write no page')
    parser.add_argument('--report', metavar='PATH',
                        help='append a markdown coverage report to PATH')
    args = parser.parse_args()

    repo = prepare_repo(args.out_dir)
    params, order = collect(repo)
    LOG.info('%d parameters over %d versions', len(params), len(order))

    overlay_path = os.path.join(args.out_dir, OVERLAY_NAME)
    with open(overlay_path) as handle:
        overlay = yaml.safe_load(handle) or {}

    documented = report_coverage(params, overlay, order, args.report)
    if not check_overlay(repo, params, overlay):
        LOG.error('Remove the entries above from %s, or fix their names',
                  overlay_path)
        return 1
    if args.check:
        if not documented:
            LOG.error('Describe the parameters above in %s', overlay_path)
            return 1
        return 0

    page = os.path.join(args.out_dir, PAGE_PATH)
    with open(page, 'w') as handle:
        handle.write(render(params, order, overlay, INTRO_NAME))
    LOG.info('Wrote %s', page)
    return 0


if __name__ == '__main__':
    sys.exit(main())
