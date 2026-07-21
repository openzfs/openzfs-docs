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
# last section of the tag index, for whatever the tagging could not place
UNTAGGED_NAME = 'Without a tag'

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
# Before 2.1 the parameters were documented in man5 with plain roff:
#   \fBzfs_arc_min\fR (ulong)
#   Default value: \fB0\fR.
OLD_MAN_PAGES = ('man/man5/zfs-module-parameters.5',
                 'man/man5/spl-module-parameters.5')
OLD_MAN_ENTRY = re.compile(
    r'^\\fB(?P<name>[a-z][a-z0-9_]*)\\fR\s*\((?P<type>[a-z0-9_ ]+)\)\s*$')
OLD_MAN_DEFAULT = re.compile(
    r'^Default value:\s*(?P<default>.*?)\s*\.?\s*$')
ROFF_MARKUP = re.compile(r'\\f[BRI]')

PERM_LABEL = {
    'ZMOD_RW': 'Dynamic',
    'ZMOD_RD': 'Prior to module load',
}

# Scopes and file names that mean the same thing as a tag already in use
TAG_ALIASES = {
    'mg': 'metaslab',
    'recv': 'receive',
    'vol': 'zvol',
    'vdev_raidz': 'raidz',
    'zevent': 'zed',
}

# Tags derived from the sources are spelled the way the curated ones are;
# these are the ones the overlay does not already spell for us.
TAG_SPELLING = {
    'brt': 'BRT',
    'ddt': 'DDT',
    'dmu': 'DMU',
    'dsl': 'DSL',
    'icp': 'ICP',
    'spl': 'SPL',
    'txg': 'TXG',
    'zap': 'ZAP',
    'zed': 'ZED',
    'zio': 'ZIO',
    'zvol': 'ZVOL',
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


def source_tags(scope, path, name):
    """Group a parameter by what the sources say it belongs to.

    The first argument of ZFS_MODULE_PARAM is the subsystem the parameter
    belongs to - it is what FreeBSD builds its sysctl node from - so use
    it, and fall back to the file for the parameters declared with the
    plain Linux macros, which carry no such argument. Nested scopes also
    yield their parent, so that "vdev" lists the mirror and disk
    parameters too.
    """
    tags = set()
    scope = scope[len('zfs_'):] if scope.startswith('zfs_') else scope
    if scope and scope != 'zfs':
        tags.add(scope)
        tags.add(scope.split('_')[0])

    stem = os.path.basename(path).rsplit('.', 1)[0].replace('-', '_')
    for prefix in ('zfs_', 'zpl_', 'spl_'):
        stem = stem[len(prefix):] if stem.startswith(prefix) else stem
    for suffix in ('_os', '_impl', '_misc'):
        stem = stem[:-len(suffix)] if stem.endswith(suffix) else stem
    if stem:
        tags.add(stem)
        tags.add(stem.split('_')[0])
    # the SPL and ICP parameters live in their own modules, say so
    for module in ('spl', 'icp'):
        if name.startswith(module + '_'):
            tags.add(module)
    return {t for t in tags if len(t) > 1}


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


def parse_old_man(repo, tag):
    """Defaults as documented before the man pages moved to mdoc in 2.1."""
    defaults = {}
    for man in OLD_MAN_PAGES:
        current = None
        for line in read(repo, tag, man).split('\n'):
            entry = OLD_MAN_ENTRY.match(line)
            if entry:
                current = entry.group('name')
                defaults[current] = {
                    'default': '',
                    'units': '',
                    'man_type': entry.group('type').strip(),
                    'in_man': True,
                }
                continue
            value = OLD_MAN_DEFAULT.match(line)
            if value and current and not defaults[current]['default']:
                text = ROFF_MARKUP.sub('', value.group('default')).strip()
                defaults[current]['default'] = text.rstrip('.')
    return defaults


def parse_man(repo, tag):
    """Defaults and units as documented in the man pages."""
    defaults = parse_old_man(repo, tag)
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


# "0=disabled, 1=enabled" - a curated range that explains every value
RANGE_ITEM = re.compile(
    r'(?:^|[,;]\s*)(?P<value>[A-Za-z0-9_.\-]{1,20})\s*=\s*')
# "33,554,432 to ``c_max``"
RANGE_BOUNDS = re.compile(r'^\s*(?P<low>\S+)\s+to\s+(?P<high>.+?)\s*$')

# What an entry of the curated overlay may hold
OVERLAY_KEYS = {'tags', 'range', 'when_to_change', 'verification', 'notes'}
TAG_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9_+.-]+$')
# a version named in the curated text; "3.2%" is a share of a pool, not one
VERSION_MENTION = re.compile(r'\bv?(?P<version>\d+\.\d+)(?:\.\d+)?\b(?!\s*%)')

SIZE_UNITS = {'b': 1, 'kb': 1024, 'kib': 1024, 'mb': 1024 ** 2,
              'mib': 1024 ** 2, 'gb': 1024 ** 3, 'gib': 1024 ** 3,
              'tb': 1024 ** 4, 'tib': 1024 ** 4}
NUMBER = re.compile(r'^(?P<value>\d+)\s*(?P<unit>[a-zA-Z%]*)$')


def normalize_default(value, units=''):
    """Compare defaults by what they mean, not by how they are written.

    The man pages changed notation in 2.1: "134,217,728 (128MB)" became
    "134217728", percentages lost their sign and sizes moved their unit
    into a separate field. Without folding that away every second
    parameter would look like its default had changed.
    """
    text = re.sub(r'\(.*?\)', '', value).replace('\\', '')
    text = text.strip().replace(',', '')
    match = NUMBER.match(text)
    if not match:
        # "10 at the time of this writing", "32  or 4" - the old pages
        # explained themselves in the value
        prose = re.match(r'^(\d+)\s*(?:[a-zA-Z%]*)\s+\S', text)
        return prose.group(1) if prose else text
    number = int(match.group('value'))
    unit = (match.group('unit') or units).lower()
    return str(number * SIZE_UNITS.get(unit, 1))


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
            'tags': source_tags('', path, name),
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
                'tags': source_tags(args[0].strip(), path, name),
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
            entry = params.setdefault(name, {'versions': [], 'defaults': {}})
            entry['versions'].append(version)
            # newest version wins, so the page describes current behaviour
            entry.update(meta)
            documented = mans[version].get(name, {})
            entry.update(documented)
            if documented.get('default'):
                entry['defaults'][version] = (
                    documented['default'],
                    normalize_default(documented['default'],
                                      documented.get('units', '')))
    return params, order


def default_runs(meta, order):
    """Group the versions by the default they document, oldest run first."""
    history = meta.get('defaults', {})
    runs = []
    for version in order:
        if version not in history:
            continue
        shown, compared = history[version]
        if runs and runs[-1][0] == compared:
            runs[-1][2].append(version)
        else:
            runs.append([compared, shown, [version]])
    return runs


def field_table(rows):
    """A two column table to be indented under a field name."""
    lines = ['.. list-table::',
             '   :widths: auto',
             '   :class: zfs-field-table',
             '']
    for left, right in rows:
        lines += ['   * - {}'.format(left), '     - {}'.format(right)]
    return lines


def default_field(meta, order):
    """One default, or a table of them when upstream changed it."""
    runs = default_runs(meta, order)
    if len(runs) < 2:
        return '``{}``'.format(meta['default']) if meta.get('default') else ''
    return field_table(
        (version_range(versions, order), '``{}``'.format(shown))
        for _, shown, versions in reversed(runs))


def range_field(text):
    """A range, or a table when the curated text explains every value."""
    if not text:
        return ''
    starts = list(RANGE_ITEM.finditer(text))
    if len(starts) < 2:
        return rst_escape(text)
    rows = []
    for index, match in enumerate(starts):
        end = (starts[index + 1].start() if index + 1 < len(starts)
               else len(text))
        meaning = text[match.end():end].strip().rstrip(',;')
        rows.append(('``{}``'.format(match.group('value')),
                     rst_escape(meaning)))
    return field_table(rows)


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


def merge_tags(params, overlay):
    """Tags of every parameter: curated ones plus the ones the sources give.

    Without this only the parameters somebody wrote notes for would appear
    in the tag index. The curated spelling wins where both exist, so that
    the source-derived "arc" joins the curated "ARC" instead of starting a
    section of its own.
    """
    spelling = dict(TAG_SPELLING)
    for entry in overlay.values():
        for tag in entry.get('tags', []):
            spelling[tag.lower()] = tag

    def canonical(tag):
        tag = TAG_ALIASES.get(tag.lower(), tag)
        return spelling.get(tag.lower(), tag)

    # The curated tags are the vocabulary somebody chose on purpose, so let
    # a parameter into them when its own name says it belongs there:
    # zfs_scrub_partial_writes lands under "scrub" without anyone writing
    # notes for it.
    vocabulary = {tag.lower(): tag for entry in overlay.values()
                  for tag in entry.get('tags', [])}

    def name_tags(name):
        padded = '_{}_'.format(name)
        return {display for word, display in vocabulary.items()
                if '_{}_'.format(word) in padded}

    curated, derived = {}, {}
    for name, meta in params.items():
        curated[name] = {canonical(tag)
                         for tag in overlay.get(name, {}).get('tags', [])}
        derived[name] = ({canonical(tag) for tag in meta.get('tags', set())}
                         | name_tags(name)) - curated[name]

    # a source tag that groups a single parameter is just a file name, keep
    # it only when it is all that parameter has
    common = defaultdict(int)
    for tags in derived.values():
        for tag in tags:
            common[tag] += 1

    tags_of = {}
    for name in params:
        useful = {tag for tag in derived[name] if common[tag] > 1}
        tags = curated[name] | useful
        if not tags:
            tags = derived[name]
        tags_of[name] = sorted(tags, key=str.lower)
    return tags_of


def render(params, order, overlay, intro_include, tags_of):
    tags = defaultdict(list)
    for name in params:
        for tag in tags_of[name]:
            tags[tag].append(name)
    # nothing may fall out of the index, even if the tagging ever fails to
    # find anything for a parameter
    untagged = sorted(name for name in params if not tags_of[name])

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
        '.. note::',
        '   Most of this page is generated from the OpenZFS sources: the list',
        '   of parameters, their types, defaults and one-line descriptions',
        '   come from the code and the man pages of each release. The tuning',
        '   advice is written by hand in ``docs/{}``.'.format(OVERLAY_NAME),
        '',
        '   If anything here is wrong, outdated or missing, please',
        '   `report it <{}issues>`__.'.format(DOCS_REPO_URL),
        '',
        '.. raw:: html',
        '',
        '   <div id="zfs-param-filter"></div>',
        '',
        '.. include:: {}'.format(intro_include),
        '',
    ]

    def tag_section(title, names):
        block = ['.. rst-class:: zfs-tag', '',
                 title, '~' * len(title), '', '.. raw:: html', '', '   <ul>']
        for name in sorted(names):
            classes = ' '.join(
                ['zfs-param'] +
                [version_class(v) for v in params[name]['versions']])
            block.append(
                '   <li class="{cls}"><a href="#{anchor}">{name}</a>'
                '</li>'.format(cls=classes, name=name,
                               anchor=name.replace('_', '-')))
        return block + ['   </ul>', '']

    if tags or untagged:
        out += ['Tags', '----', '',
                'The list of parameters is large and resists hierarchical',
                'representation. Each parameter is tagged with keywords for',
                'frequent searches.', '']
        for tag in sorted(tags, key=str.lower):
            out += tag_section(tag, tags[tag])
        if untagged:
            out += tag_section(UNTAGGED_NAME, untagged)

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
            ('Default', default_field(meta, order)),
            ('Units', meta.get('units', '')),
            ('Range', range_field(curated.get('range', ''))),
            ('Change', PERM_LABEL.get(meta['perm'], '')),
            ('Tags', ', '.join(
                '`{tag} <#{anchor}>`__'.format(
                    tag=tag, anchor=tag.lower().replace('_', '-'))
                for tag in tags_of[name])),
        ]
        for label, value in fields:
            if not value:
                continue
            if isinstance(value, str):
                out.append(':{}: {}'.format(label, value))
            else:  # a table, which has to start on its own line
                out.append(':{}:'.format(label))
                out += ['   ' + line if line else '' for line in value]
                out.append('')
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


def report_coverage(params, overlay, order, tags_of, report_path=None):
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

    untagged = sorted(name for name, tags in tags_of.items() if not tags)
    if untagged:
        LOG.warning('%d parameters ended up under no tag at all, the index '
                    'lists them under "%s": %s',
                    len(untagged), UNTAGGED_NAME, ', '.join(untagged))

    if report_path:
        write_report(report_path, undocumented, uncurated, untagged,
                     missing, total)
    return not undocumented


def write_report(path, undocumented, uncurated, untagged, missing, total):
    """Markdown summary, meant for $GITHUB_STEP_SUMMARY."""
    lines = ['## OpenZFS module parameter coverage', '',
             '{} of {} parameters have no curated notes in `{}`.'.format(
                 missing, total, OVERLAY_NAME), '']
    if undocumented:
        lines += ['### Documented nowhere', '',
                  'These have no upstream description either, so the page '
                  'can only show their name:', '']
        lines += ['- `{}`'.format(name) for name in undocumented] + ['']
    if untagged:
        lines += ['### Under no tag', '',
                  'The tag index lists these under "{}", so they are still '
                  'reachable, but they belong somewhere better:'.format(
                      UNTAGGED_NAME), '']
        lines += ['- `{}`'.format(name) for name in untagged] + ['']
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


class StrictLoader(yaml.SafeLoader):
    """A loader that refuses duplicate keys.

    PyYAML keeps the last of them, so a parameter or a field written twice
    would silently lose whatever was said the first time.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, 'duplicate key {!r}'.format(key),
                    key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def plain_number(text):
    """The integer a curated bound or value spells, if it spells one."""
    text = re.sub(r'[`,_]', '', str(text)).strip()
    return int(text) if re.fullmatch(r'\d+', text) else None


def check_entry(name, entry, vocabulary=frozenset()):
    """Everything that is wrong with one curated entry."""
    problems = []
    for key in sorted(set(entry) - OVERLAY_KEYS):
        problems.append('unknown key {!r}, expected one of {}'.format(
            key, ', '.join(sorted(OVERLAY_KEYS))))
    for key, value in sorted(entry.items()):
        if key not in OVERLAY_KEYS:
            continue
        if key == 'tags':
            if not isinstance(value, list):
                problems.append('tags must be a list, got {}'.format(
                    type(value).__name__))
                continue
            if len(value) != len(set(value)):
                problems.append('duplicate tags: {}'.format(value))
            for tag in value:
                if not isinstance(tag, str) or not TAG_PATTERN.match(tag):
                    problems.append('malformed tag {!r}'.format(tag))
            # "ZIO_scheduler" once arrived here as "Z" plus "IO_scheduler",
            # a tag that a line break had torn in two
            for first in value:
                for second in value:
                    if (first is not second and isinstance(first, str)
                            and isinstance(second, str)
                            and first + second in vocabulary):
                        problems.append(
                            'tags {!r} and {!r} join into {!r}, a tag torn '
                            'in two?'.format(first, second, first + second))
        elif not isinstance(value, str):
            problems.append('{} must be text, got {}'.format(
                key, type(value).__name__))
        elif not value.strip():
            problems.append('{} is empty'.format(key))
    return problems


def check_range(name, entry, meta):
    """A curated range that disagrees with the documented default."""
    curated = entry.get('range')
    if not curated or not isinstance(curated, str) or not meta.get('default'):
        return None
    default = plain_number(normalize_default(meta['default'],
                                             meta.get('units', '')))
    if default is None:
        return None

    items = list(RANGE_ITEM.finditer(curated))
    if len(items) > 1:
        values = [plain_number(item.group('value')) for item in items]
        if None not in values and default not in values:
            return 'default {} is not one of the documented values {}'.format(
                default, values)
        return None

    bounds = RANGE_BOUNDS.match(curated)
    if not bounds:
        return None
    low = plain_number(bounds.group('low'))
    high = plain_number(bounds.group('high'))
    # 0 is the usual "pick a value yourself" default and is rarely part of
    # the range a user may set
    if default == 0 and low is not None and low > 0:
        return None
    if low is not None and default < low:
        return 'default {} is below the documented range "{}"'.format(
            default, curated)
    if high is not None and default > high:
        return 'default {} is above the documented range "{}"'.format(
            default, curated)
    return None


def check_versions(entry, order):
    """Releases named in the curated text that OpenZFS never had."""
    known = set(order)
    unknown = set()
    for key in ('notes', 'when_to_change', 'verification', 'range'):
        value = entry.get(key)
        if not isinstance(value, str):
            continue
        for match in VERSION_MENTION.finditer(value):
            if match.group('version') not in known:
                unknown.add(match.group('version'))
    return sorted(unknown)


def check_overlay(repo, params, overlay, order):
    """Fail on curated entries for parameters that never existed."""
    unknown = sorted(set(overlay) - set(params))
    if unknown:
        LOG.error('Overlay describes %d unknown parameters: %s',
                  len(unknown), ', '.join(unknown))

    vocabulary = {tag for entry in overlay.values()
                  if isinstance(entry, dict)
                  for tag in entry.get('tags', [])
                  if isinstance(tag, str)}

    broken = False
    for name in sorted(overlay):
        entry = overlay[name]
        if not isinstance(entry, dict):
            LOG.error('%s: entry must be a mapping, got %s',
                      name, type(entry).__name__)
            broken = True
            continue
        for problem in check_entry(name, entry, vocabulary):
            LOG.error('%s: %s', name, problem)
            broken = True
        meta = params.get(name)
        if meta:
            mismatch = check_range(name, entry, meta)
            if mismatch:
                LOG.warning('%s: %s', name, mismatch)
        for version in check_versions(entry, order):
            LOG.warning('%s: mentions OpenZFS %s, which is not a release '
                        'this page knows about', name, version)

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
    return not unknown and not broken


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
    try:
        with open(overlay_path) as handle:
            overlay = yaml.load(handle, StrictLoader) or {}
    except yaml.YAMLError as error:
        LOG.error('Cannot read %s: %s', overlay_path, error)
        return 1

    tags_of = merge_tags(params, overlay)
    documented = report_coverage(params, overlay, order, tags_of,
                                 args.report)
    if not check_overlay(repo, params, overlay, order):
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
        handle.write(render(params, order, overlay, INTRO_NAME, tags_of))
    LOG.info('Wrote %s', page)
    return 0


if __name__ == '__main__':
    sys.exit(main())
