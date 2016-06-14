import os
import sys

from git import Repo
from enchant.checker import SpellChecker

if len(sys.argv) != 2:
    print "Usage: %s [path]" % sys.argv[0]
    sys.exit()

repo_path = sys.argv[1]

repo = Repo(repo_path)
files = repo.git.ls_files()
file_list = files.split('\n')

spell_checker = SpellChecker("en_US")

for fname in file_list:
    if fname[-3:] != '.py' or "migration" in fname:
        continue
    file = open(os.path.join(repo_path, fname))
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
            spell_checker.set_text(comment)
            for err in spell_checker:
                print "\033[31mERROR: %s\033[0m" % err.word

