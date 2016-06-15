# -*- coding: utf-8 -*-
import os
import sys
import getopt
import re

from git import Repo
from enchant.checker import SpellChecker


PROG_NAME = "comment-review"

COLOR_OUTPUT = {
        "filename":"\033[34m\033[1m--- File: {} ---\033[0m\n",
        "line_num":"\033[32m\033[1m{}: \033[0m",
        "error":"\033[31mERROR: {}\033[0m\n"
        }

NO_COLOR_OUTPUT = {
        "filename":"--- File: {} ---\n",
        "line_num":"{}: ",
        "error":"ERROR: {}\n"
        }

def usage():
    print('Usage:\n\t{}\t{} {}'.format(PROG_NAME, "", "run reviewer on files under git version control in current directory"))
    print('\n\t{:10} {:20} {:30}'.format(PROG_NAME, "[path/to/folder]", "run reviewer on files under git version control in specified directory"))
    print('Options:')
    print('\t{:2} {:15} {:10} {:30}'.format("-m", "--comments-only", "", "print only comments, without code"))
    print('\t{:2} {:15} {:10} {:30}'.format("-n", "--no-color", "", "disable color"))
    print('\t{:2} {:15} {:10} {:30}'.format("-a", "--all-files", "", "run reviewer on all files in directory, not just those under version control"))
    print('\t{:2} {:10} {:15} {:30}'.format("-o", "--output", "[filename]", "pipe output to a file"))

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
    out_strings = COLOR_OUTPUT

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
            out_strings = NO_COLOR_OUTPUT
            is_no_color = True
        elif opt in ("-a", "--all-files"):
            is_all_files = True
        elif opt in ("-o", "--output"):
            output_filename = arg
            out_strings = NO_COLOR_OUTPUT # if writing to file, don't use colour
    if len(args) > 0:
        folder = "".join(args)
    
    if not os.path.exists(folder) or not os.path.isdir(folder):
        sys.exit('ERROR: {} was not found or is not a folder!'.format(folder))

    if output_filename != None:
        out_file = open(output_filename, "w+")
    else:
        out_file = sys.stdout

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
        line_num = 1
        comments = []
        current_comment = ''
        current_line = out_strings ['line_num'].format(line_num)
        flag = 0
        for character in content:
            current_line += character
            if character == '#' and flag == 0:
                flag = 1
                current_comment += out_strings ['line_num'].format(line_num)
            elif character == '\n':
                line_num += 1
                if flag:
                    flag = 0
                    current_comment += '\n'
                    if is_comments_only == True:
                        comments.append(current_comment)
                    else:
                        comments.append(current_line)
                    current_comment = ''
                current_line = out_strings ['line_num'].format(line_num)
            if flag:
                current_comment += character
        if len(comments) > 0:
            out_file.write(out_strings ['filename'].format(fname))
            for comment in comments:
                out_file.write(comment)
                spell_checker.set_text(removeURLs(comment))
                for err in spell_checker:
                    out_file.write(out_strings ['error'].format(err.word))

    if output_filename != None:
        out_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])
