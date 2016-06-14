# -*- coding: utf-8 -*-
import os
import sys
import getopt
import re

from git import Repo
from enchant.checker import SpellChecker


PROG_NAME = "comment-review"

def usage():
    print('Usage:\n\t%10s %20s %30s' % (PROG_NAME, "", "run reviewer on files under git version control in current directory"))
    print('\n\t%10s %20s 30s' % (PROG_NAME, "[path/to/folder]", "run reviewer on files under git version control in specified directory"))
    print('Options:')
    print('\t%-2s %-10s %-10s %-30s' % ("-m", "--comments-only", "", "print only comments, without code"))
    print('\t%-2s %-10s %-10s %-30s' % ("-n", "--no-color", "", "disable color"))
    print('\t%-2s %-10s %-10s %-30s' % ("-a", "--all-files", "", "run reviewer on all files in directory, not just those under version control"))
    print('\t%-2s %-10s %-10s %-30s' % ("-o", "--output", "[filename]", "pipe output to a file"))

def removeURLs(txt):
    regex = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
    ret = re.sub(regex, '', txt)
    return ret

def main(argv):

    # defaults
    folder = '.' 
    is_comments_only = False
    is_no_color = False
    is_all_files = False
    output_filename = None

    # command-line arguments
    try:
        opts, args = getopt.gnu_getopt(argv, "hmnao:", ["help", "comments-only", "no-color", "all-files", "output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-m", "--comments-only"):
            is_comments_only = True
        elif opt in ("-n", "--no-color"):
            is_no_color = True
        elif opt in ("-a", "--all-files"):
            is_all_files = True
        elif opt in ("-o", "--output"):
            output_filename = arg
    if len(args) > 0:
        folder = "".join(args)
    
    if not os.path.exists(folder) or not os.path.isdir(folder):
        sys.exit('ERROR: %s was not found or is not a folder!' % folder)

    repo = Repo(folder)
    files = repo.git.ls_tree('--name-only', r="master")
    file_list = files.split('\n')
    spell_checker = SpellChecker("en_US")

    if output_filename:
        try:
            f = open(output_filename,"w")
        finally:
            f.close()

    for fname in file_list:
        if not fname.endswith('.py') or "migration" in fname:
            continue
        file = open(os.path.join(folder, fname))
        content = file.read()
        comments = []
        current_comment = ''
        flag = 0
        line_num = 1
        for character in content:
            if character == '#':
                flag = 1
                current_comment += "\033[32m\033[1m{}: \033[0m".format(line_num)
            elif character == '\n':
                line_num += 1
                if flag:
                    flag = 0
                    comments.append(current_comment)
                    current_comment = ''
            if flag:
                current_comment += character
        if len(comments) > 0:
            print "\033[34m\033[1m--- File: %s ---\033[0m" % fname
            for comment in comments:
                print comment
                spell_checker.set_text(removeURLs(comment))
                for err in spell_checker:
                    print "\033[31mERROR: %s\033[0m" % err.word


if __name__ == "__main__":
    main(sys.argv[1:])
