#!/usr/bin/env python3
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2020 George Melikov <mail@gmelikov.ru>
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys

import git

LOG = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

zfs_repo_url = 'https://github.com/openzfs/zfs/'

MAN_SECTIONS = {
    '1': 'User Commands',
    '2': 'System Calls',
    '3': 'C Library Functions',
    '4': 'Devices and Special Files',
    '5': 'File Formats and Conventions',
    '6': 'Games',
    '7': 'Miscellaneous',
    '8': 'System Administration Commands',
}

MAN_SECTION_DIR = 'man'
MAN_SECTION_NAME = 'Man Pages'

BUILD_DIR = '_build'
MAN_BUILD_DIR = os.path.join(BUILD_DIR, 'man')

ZFS_GIT_REPO = 'https://github.com/openzfs/zfs.git'
TAG_REGEX = re.compile(
    r'zfs-(?P<version>'
    r'(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<fix>[0-9]+))')

LINKS_REGEX_TEMPLATE = (r'<a(?P<href_place> )class=\"Xr\"(?P<title>.*?)>%s'
                        r'\((?P<num>[1-9])\)<\/a>')
LINKS_FINAL_REGEX = (r'<a href="../\g<num>/\g<name>.\g<num>.html" class="Xr"'
                     r'>\g<name>(\g<num>)</a>')


def add_hyperlinks(out_dir, version, pages):
    all_pages = []
    for _section, section_pages in pages.items():
        all_pages.extend([
            os.path.splitext(page)[0] for page in section_pages])
    tmp_regex = '(?P<name>' + "|".join(all_pages) + ')'
    html_regex = re.compile(
        LINKS_REGEX_TEMPLATE % tmp_regex, flags=re.MULTILINE)

    for section, pages in pages.items():
        for page in pages:
            file_path = os.path.join(
                out_dir, MAN_BUILD_DIR,
                version, 'man' + section, page + '.html')
            with open(file_path, "r") as f:
                text = f.read()
            new_text = re.sub(html_regex, LINKS_FINAL_REGEX, text)
            if text != new_text:
                with open(file_path, "w") as f:
                    LOG.debug('Crosslinks detected in %s, generate',
                              file_path)
                    text = f.write(new_text)


def run(in_dir, out_dir, version, tag):
    pages = {num: [] for num in MAN_SECTIONS}
    for subdir, dirs, _ in os.walk(in_dir):
        for section in dirs:
            section_num = section.replace('man', '')
            section_suffix = '.' + section_num
            if section_num not in MAN_SECTIONS:
                continue
            out_section_dir = os.path.join(
                out_dir, MAN_BUILD_DIR, version, section)
            os.makedirs(out_section_dir, exist_ok=True)
            for page in os.listdir(os.path.join(subdir, section)):
                if not (page.endswith(section_suffix) or
                        page.endswith(section_suffix + '.in')):
                    continue
                LOG.debug('Generate %s page', page)
                stripped_page = page.rstrip('.in')
                page_file = os.path.join(out_section_dir,
                                         stripped_page + '.html')
                page_file_txt = os.path.join(out_section_dir,
                                             stripped_page + '.txt')
                with open(page_file, "w") as f:
                    subprocess.run(
                        ['mandoc', '-T', 'html', '-O', 'fragment',
                         os.path.join(subdir, section, page)], stdout=f,
                        check=True)
                # For LLM, generate only master version to minimize size
                if version == 'master':
                    try:
                        with open(page_file_txt, "w") as f:
                            subprocess.run(
                                ['mandoc', '-T', 'markdown',
                                 os.path.join(subdir, section, page)], stdout=f,
                                check=True)
                    except subprocess.CalledProcessError:
                        LOG.warning('Could not convert %s to md, just copy...', page_file_txt)
                        shutil.copy(os.path.join(subdir, section, page), page_file_txt)

                pages[section_num].append(stripped_page)
        break

    man_path = os.path.join(out_dir, MAN_SECTION_DIR, version)
    os.makedirs(man_path, exist_ok=True)

    # Index for version
    with open(os.path.join(man_path, 'index.rst'), "w") as f:
        f.write("""\
.. THIS FILE IS AUTOGENERATED, DO NOT EDIT!

:llms-txt-ignore: true
:github_url: {zfs_repo_url}blob/{tag}/man/

{name}
{name_sub}
.. toctree::
    :maxdepth: 1
    :glob:

    */index
            """.format(zfs_repo_url=zfs_repo_url,
                       name=version,
                       tag=tag,
                       name_sub="=" * len(version)))

    for section_num, section_pages in pages.items():
        if not section_pages:
            continue
        rst_dir = os.path.join(out_dir, MAN_SECTION_DIR, version, section_num)
        os.makedirs(rst_dir, exist_ok=True)
        section_name = MAN_SECTIONS[section_num]
        section_name_with_num = '{name} ({num})'.format(
            name=section_name, num=section_num)
        with open(os.path.join(rst_dir, 'index.rst'), "w") as f:
            f.write("""\
.. THIS FILE IS AUTOGENERATED, DO NOT EDIT!

:llms-txt-ignore: true
:github_url: {zfs_repo_url}blob/{tag}/man/man{section_num}/

{name}
{name_sub}
.. toctree::
    :maxdepth: 1
    :glob:

    *
                """.format(zfs_repo_url=zfs_repo_url,
                           section_num=section_num,
                           name=section_name_with_num,
                           tag=tag,
                           name_sub="=" * len(section_name_with_num),))

        for page in section_pages:
            # for LLM
            if version == 'master':
                llm_source_dst = os.path.join(
                    out_dir, BUILD_DIR, 'html', '_sources', 'man', version, section_num)
                os.makedirs(llm_source_dst, exist_ok=True)
                os.rename(
                    os.path.join(out_dir, MAN_BUILD_DIR, version,
                                 f"man{section_num}", f"{page}.txt"),
                    os.path.join(llm_source_dst, page + '.md.txt'))
            with open(os.path.join(rst_dir, page + '.rst'), "w") as f:
                f.write("""\
.. THIS FILE IS AUTOGENERATED, DO NOT EDIT!

{tags}
:github_url: {zfs_repo_url}blob/{tag}/man/man{section_num}/{name}

{name}
{name_sub}
.. raw:: html

   <div class="man_container">

.. raw:: html
   :file: ../../../{build_dir}/{version}/man{section_num}/{name}.html

.. raw:: html

   </div>
                    """.format(zfs_repo_url=zfs_repo_url,
                               tags=":llms-txt-ignore: true" if version != 'master' else "",
                               name=page,
                               build_dir=MAN_BUILD_DIR,
                               version=version,
                               tag=tag,
                               section_num=section_num,
                               name_sub="=" * len(page)))
    add_hyperlinks(out_dir, version, pages)


def gen_index(out_dir, tags):
    # Global index
    with open(os.path.join(os.path.join(out_dir, MAN_SECTION_DIR),
                           'index.rst'), "w") as f:
        f.write("""\
.. THIS FILE IS AUTOGENERATED, DO NOT EDIT!

{name}
{name_sub}
.. toctree::
    :maxdepth: 1
    :glob:

""".format(name=MAN_SECTION_NAME, name_sub="=" * len(MAN_SECTION_NAME))
        )
        for ver in reversed(tags.keys()):
            f.write("""\
    {ver}/index
""".format(ver=ver))


def prepare_repo(path):
    # TODO(gmelikov): check for actual tags fetch on remote repo updates
    repo_dir = os.path.join(path, BUILD_DIR)
    os.makedirs(repo_dir, exist_ok=True)
    try:
        repo = git.Repo(os.path.join(repo_dir, 'zfs'))
        LOG.info('zfs repo already cloned')
        for remote in repo.remotes:
            remote.fetch(tags=None)
    except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError):
        LOG.info('Clone zfs repo...')
        git.Git(repo_dir).clone(ZFS_GIT_REPO)


def iterate_versions(out_dir):
    repo_path = os.path.join(BUILD_DIR, 'zfs')
    git_cmd = git.Git(repo_path)
    repo = git.Repo(os.path.join(BUILD_DIR, 'zfs'))
    # sort tags, some versions are not semvers so we'll use latest ones
    # (for ex. 0.6.5.11)
    repo_tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    tags = {}
    for tag in repo_tags:
        tag = str(tag)
        if 'rc' in tag:
            LOG.debug("Skip rc version %s", tag)
            continue
        version = TAG_REGEX.match(tag)
        if not version:
            LOG.info("Cannot parse %s version, skipping...", tag)
            continue
        ver_dict = {k: int(v) if 'version' not in k else v
                    for k, v in version.groupdict().items()}
        # ignore pre-0.6 versions
        if ver_dict['major'] > 0 or ver_dict['minor'] > 5:
            # get only latest minor versions
            tags[f'v{ver_dict["major"]}.{ver_dict["minor"]}'] = tag

    tags['master'] = 'master'

    LOG.info('Tags to build: %r', tags)

    gen_index(out_dir, tags)

    for version, tag in tags.items():
        git_cmd.checkout(tag)
        run(os.path.join(repo_path, 'man'), out_dir, version, tag)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir',
                        help='Sphinx docs dir')
    args = parser.parse_args()

    os.makedirs(os.path.join(args.out_dir, MAN_SECTION_DIR), exist_ok=True)

    prepare_repo(args.out_dir)

    iterate_versions(args.out_dir)


if __name__ == '__main__':
    main()
