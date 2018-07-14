#!/usr/bin/env python

import os
import argparse

from pathlib import Path
from git import Repo
from enchant.checker import SpellChecker


class Logger:

    def __init__(self, color=True):
        self.color = color

    def print_filename(self, s):
        if self.color:
            print(f"\033[34m\033[1m--- File: {s} ---\033[0m")
        else:
            print(f"--- File: {s} ---")

    def print_comment(self, line_num, s):
        if self.color:
            print(f"\033[32m\033[1m{line_num}: \033[0m{s}")
        else:
            print(f"{line_num}: {s}")

    def print_error(self, s):
        if self.color:
            print(f"\033[31mERROR: {s}\033[0m")
        else:
            print(f"ERROR: {s}")


def parse_arguments():

    parser = argparse.ArgumentParser(
                 description='Inspect comments with possible spelling errors.')
    parser.add_argument('--color', dest='color', action='store_true')
    parser.add_argument('--no-color', dest='color', action='store_false')
    parser.set_defaults(color=True)
    parser.add_argument('--branch', type=str, default='master',
                        help='branch of git repo to inspect; default is master')
    parser.add_argument('repo_path', type=str,
                        help='path to git repository to inspect')
    return parser.parse_args()


def main(color=True, repo_path='.', branch='master'):

    logger = Logger(color=color)
    spell_checker = SpellChecker("en_US")
    repo = Repo(repo_path)
    fnames = repo.git.ls_tree('--name-only', r=branch).split('\n')
    fnames_py = [f for f in fnames
                 if Path(f).suffix == '.py' and "migration" not in f]

    for fname in fnames_py:

        with open(os.path.join(repo_path, fname)) as f:
            content = f.read()

        comments = []
        comment = ''
        comment_line_num = 0
        in_comment = False
        line_num = 1

        for ch in content:
            if ch == '#':
                in_comment = True
                comment_line_num = line_num
            elif ch == '\n':
                line_num += 1
                if in_comment:
                    in_comment = False
                    comments.append((comment_line_num, comment))
                    comment = ''
            if in_comment:
                comment += ch

        if len(comments) > 0:
            logger.print_filename(fname)
            for (line_num, comment) in comments:
                logger.print_comment(line_num, comment)
                spell_checker.set_text(comment)
                for error in spell_checker:
                    logger.print_error(error.word)


if __name__ == "__main__":
    args = parse_arguments()
    main(**vars(args))
