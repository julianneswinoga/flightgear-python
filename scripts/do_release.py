#!/usr/bin/env python3

import signal
import inspect
from collections import namedtuple
from typing import Optional, Callable, List

import sh
import git
from packaging import version

action_history = []
named_action = namedtuple('NamedAction', ['description', 'fn'])
check_yn = lambda x: x[0].lower() in 'yn'
conv_yn = lambda x: x[0].lower()


def check_environment():
    for prog_name in ('auto-changelog', 'poetry'):
        if sh.which(prog_name) is None:
            print(f'Could not find {prog_name} in PATH! I need it!')
            exit(1)


def apply_actions(actions: List[named_action]):
    prefix_str = '\r\n - '
    actions_str = prefix_str + prefix_str.join(a.description for a in actions)
    yn = get_user_input(f'Would you like to apply the following actions:{actions_str}\r\n[y/n]',
                        check_yn, conv_yn)
    if yn == 'y':
        for act in actions:
            print(f'Applying action {act.description}')
            act.fn()
            action_history.append(act)
        actions.clear()
        return True
    else:
        return False


def print_action_history(msg_if_print: str):
    if len(action_history) > 0:
        print(msg_if_print)
        for i, act in enumerate(action_history):
            print(f'{i}: {act.description} {act.fn}:\n{inspect.getsource(act.fn).strip()}')


def clean_exit(exit_code: int):
    print_action_history('Exiting after actions were performed:')
    exit(exit_code)


def handler_stop_signals(signum, frame):
    print('\r\n\r\n')
    print_action_history('Unexpected exit after actions were performed:')
    print('Exiting.')
    if signum is not None or frame is not None:
        # Exiting from an actual signal, not exception handler
        exit(1)


def get_git_info():
    repo = git.Repo('.', search_parent_directories=True)
    index = repo.index
    git_root = repo.git.rev_parse("--show-toplevel")
    all_tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = all_tags[-1] if len(all_tags) > 0 else None
    return {
        'repo': repo,
        'index': index,
        'root': git_root,
        'latest_tag': latest_tag,
    }


def get_user_input(prompt: str, check_fn: Optional[Callable] = None, conv_fn: Optional[Callable] = None):
    while True:
        val_str = input(prompt + ' >')
        if check_fn is None or (len(val_str) > 0 and check_fn(val_str)):
            break
        print('Invalid input')
        continue
    if conv_fn is not None:
        val = conv_fn(val_str)
    else:
        val = val_str
    return val


def gen_auto_changelog(auto_file: str, current_version: str):
    auto_changelog_cmd = sh.auto_changelog.bake(
        template='./scripts/changelog_template.hbs',
        output=auto_file,
        commit_limit='false',
        starting_version=current_version,
    )
    # if current_version is not None:
    #     auto_changelog_cmd = auto_changelog_cmd.bake(starting_version=current_version)
    print('Running auto_changelog command:', auto_changelog_cmd)
    auto_changelog_cmd()


def merge_auto_and_real_changelog(auto_file: str, real_file: str, delete_auto=True):
    print(f'Merging auto changelog {auto_file} and real changelog {real_file}')
    with open(auto_file, 'r') as f:
        auto_changelog = f.read()
    if delete_auto:
        sh.rm(auto_file)

    try:
        with open(real_file, 'r') as f:
            existing_changelog = f.read()
    except FileNotFoundError:
        existing_changelog = None
    with open(real_file, 'w') as f:
        f.write(auto_changelog)
        if existing_changelog is not None:
            f.write('\n')
            f.write(existing_changelog)
    get_user_input('Please edit the changelog entry, press enter when done')


def main():
    check_environment()

    git_info = get_git_info()
    print(f"root dir is {git_info['root']}")
    if git_info['repo'].is_dirty():
        print('Can\'t operate on a dirty repo. Please commit any working changes.')
        clean_exit(1)

    actions = []
    if git_info['latest_tag'] is None:
        # First release!
        yn = get_user_input('No tags yet, would you like to create 1.0.0? [y/n]',
                            check_yn, conv_yn)
        if yn == 'n':
            clean_exit(0)
        poetry_bump_str = '1.0.0'
    else:
        # version increment
        poetry_set_version_action = named_action(
            f"Set poetry version to {git_info['latest_tag']} (latest tag)",
            lambda: sh.poetry.version('-q', git_info['latest_tag'])
        )
        actions.append(poetry_set_version_action)
        if not apply_actions(actions):
            clean_exit(0)

        is_semver = lambda x: isinstance(version.parse(x), version.Version)
        is_increment = lambda x: version.parse(x) > version.parse(str(git_info['latest_tag']))
        poetry_version_rules = ('patch', 'minor', 'major')
        check_semver_or_rule = lambda x: (is_semver(x) and is_increment(x)) or x in poetry_version_rules
        poetry_bump_str = get_user_input(f"Latest tag is {git_info['latest_tag']}, "
                                         f"input the new tag or bump rule (one of {poetry_version_rules})",
                                         check_semver_or_rule)

    # make an empty commit that the tag will apply to
    git_empty_commit_action = named_action(
        'create empty commit',
        lambda: git_info['index'].commit(f'Autogenerated release {poetry_bump_str}')
    )
    poetry_set_version_action = named_action(
        f'Set poetry version to {poetry_bump_str}',
        lambda: sh.poetry.version('-q', poetry_bump_str)
    )
    actions.append(git_empty_commit_action)
    actions.append(poetry_set_version_action)
    if not apply_actions(actions):
        clean_exit(0)

    poetry_version_str = sh.poetry.version('-s').strip()

    # Tag the current commit so that auto_changelog can grab the details
    git_create_tag_action_1 = named_action(
        f"Create tag {poetry_version_str} @ {git_info['repo'].head.commit.hexsha}",
        lambda: git_info['repo'].create_tag(poetry_version_str, message=f'Automatic tag "{poetry_version_str}"')
    )
    actions.append(git_create_tag_action_1)
    if not apply_actions(actions):
        clean_exit(0)

    with sh.pushd(git_info['root']):
        auto_changelog = './auto_CHANGELOG.md'
        real_changelog = './CHANGELOG.md'
        gen_auto_changelog(auto_changelog, current_version=poetry_version_str)
        merge_auto_and_real_changelog(auto_changelog, real_changelog)
        git_add_changelog_action = named_action(
            f'Add {real_changelog} changes to git',
            lambda: git_info['repo'].git.add(real_changelog)
        )
        actions.append(git_add_changelog_action)

    print('Unstaged files:')
    for item in git_info['index'].diff(None):
        print(f'\t{item.a_path}')
    print('Untracked files:')
    for item in git_info['repo'].untracked_files:
        print(f'\t{item}')

    git_amend_action = named_action(
        f'Amend all changes to latest commit',
        lambda: git_info['repo'].git.commit('--all', '--amend', '--no-edit')
    )
    actions.append(git_amend_action)
    if not apply_actions(actions):
        clean_exit(0)

    old_auto_tag = next((t.commit for t in git_info['repo'].tags if t.name == poetry_version_str), None)
    if old_auto_tag is None:
        raise ValueError(f'Could not find old auto-tag {poetry_version_str}')
    git_delete_tag_action = named_action(
        f'Delete tag {poetry_version_str} @ {old_auto_tag}',
        lambda: git_info['repo'].delete_tag(poetry_version_str)
    )
    git_create_tag_action_2 = named_action(
        f"Create tag {poetry_version_str} @ {git_info['repo'].head.commit.hexsha}",
        lambda: git_info['repo'].create_tag(poetry_version_str, message=f'Automatic tag "{poetry_version_str}"')
    )
    actions.append(git_delete_tag_action)
    actions.append(git_create_tag_action_2)
    if not apply_actions(actions):
        clean_exit(0)

    print_action_history('\r\nRan the following actions:')
    print(f'\r\nYou should now run `git push origin master && git push origin $(git describe)`')


if __name__ == '__main__':
    import logging, sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)
    try:
        main()
    except Exception as e:
        handler_stop_signals(None, None)
        raise e
