import re
import sys
import os
import ast


# [S001] line too long
def line_too_long_error(index, line_in):
    if len(line_in) > 79:
        err = 'S001 Too long'
        output.append(f'Line {index}: {err}')


# [S002] Indentation is not a multiple of four
def indent_error(index, line_in):
    if (len(line_in) - len(line_in.lstrip(' '))) % 4 != 0:
        err = 'S002 Indentation is not a multiple of four'
        output.append(f'Line {index}: {err}')


# [S003] Unnecessary semicolon after a statement (note that semicolons are acceptable in comments);
def semicolon_error(index, line_in):
    if re.search(r"; *#", line_in) or (re.search(r"; *$", line_in) and (re.search(r"#.*;", line_in) is None)):
        err = 'S003 Unnecessary semicolon'
        output.append(f'Line {index}: {err}')


# [S004] Less than two spaces before inline comments;
def inline_comments_error(index, line_in):
    if re.search(r".+#.*$", line_in):
        if re.search(r" {2,}#.*$", line_in) is None:
            err = 'S004 At least two spaces required before inline comments'
            output.append(f'Line {index}: {err}')


# [S005] TODO found (in comments only and case-insensitive);
def todo_error(index, line_in):
    if re.search(r"#.*TODO.*$", line_in, re.IGNORECASE):
        err = 'S005 TODO found'
        output.append(f'Line {index}: {err}')


# [S006] More than two blank lines preceding a code line (applies to the first non-empty line).
def blank_line_error(index, line_in, lines):
    if line_in != '' and index > 4:
        if lines[index - 2] == '' and lines[index - 3] == '' and lines[index - 4] == '':
            err = 'S006 More than two blank lines used before this line'
            output.append(f'Line {index}: {err}')


# [S007] Too many spaces after construction_name (def or class);
def space_before_class_error(index, line_in):
    if re.search(r'^class {2}', line_in):
        err = "S007 Too many spaces after 'class'"
        output.append(f'Line {index}: {err}')
    if re.search(r'^ *def {2}', line_in):
        err = "S007 Too many spaces after 'def'"
        output.append(f'Line {index}: {err}')


# [S008] Class name class_name should be written in CamelCase;
def class_name_error(index, line_in):
    if re.search(r'^class +[a-z]', line_in):
        class_name = re.search(r'\w+ *:$', line_in)
        class_name = class_name[0].split()[0]
        err = f"S008 Class name '{class_name}' should use CamelCase"
        output.append(f'Line {index}: {err}')


# [S009] Function name function_name should be written in snake_case.
# [S010] Argument name arg_name should be written in snake_case;
def func_error(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            if re.search(r'[A-Z]', func_name):
                err = f"S009 Function name '{func_name}' should use snake_case"
                output.append(f'Line {node.lineno}: {err}')
            for arg in node.args.args:
                if re.match('[A-Z]', arg.arg):
                    err = f"S010 Argument name '{arg.arg}' should be written in snake_case"
                    output.append(f'Line {node.lineno}: {err}')
            for tp in node.args.defaults:
                if isinstance(tp, ast.List) or isinstance(tp, ast.Tuple) or isinstance(tp, ast.Dict):
                    err = f"S012 Default argument value is mutable"
                    output.append(f'Line {node.lineno}: {err}')
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and re.match('[A-Z]', target.id):
                    err = f"S011 Variable '{target.id}' should be written in snake_case"
                    output.append(f'Line {node.lineno}: {err}')
    # if re.search(r"def +[_a-z]*[A-Z]", line_in):
    #     func_name = re.search(r" +\w+ *\(", line_in)
    #     func_name = func_name[0].split()[0]
    #     if func_name[-1] == '(':
    #         func_name = func_name[:-1]


def sort_by_line_num(el):
    lin_no = int(re.search(r'\d+:', el)[0][:-1])
    err_no = int(re.search(r'[Ss]0..', el)[0][-2:])
    return lin_no, err_no


def check_for_err(path):
    with open(path, 'r') as f:
        read = f.read()
        lines = read.splitlines()
        tree = ast.parse(read)
        for i, line in enumerate(lines, start=1):
            # LineTooLongError
            line_too_long_error(i, line)
            # [S002] Indentation is not a multiple of four
            indent_error(i, line)
            # [S003] Unnecessary semicolon after a statement (note that semicolons are acceptable in comments);
            semicolon_error(i, line)
            # [S004] Less than two spaces before inline comments;
            inline_comments_error(i, line)
            # [S005] TODO found (in comments only and case-insensitive);
            todo_error(i, line)
            # [S006] More than two blank lines preceding a code line (applies to the first non-empty line).
            blank_line_error(i, line, lines)
            # [S007] Too many spaces after construction_name (def or class);
            space_before_class_error(i, line)
            # [S008] Class name class_name should be written in CamelCase;
            class_name_error(i, line)
            # [S009] Function name function_name should be written in snake_case.
        func_error(tree)
        # print out the final output
        output.sort(key=sort_by_line_num)
        for _ in output:
            print(path + ":", _)
        output.clear()


if __name__ == "__main__":
    # input the file/folder path
    output = []
    path_input = sys.argv[1]
    # check if it is a single file or a folder
    if os.path.isfile(path_input):
        if os.path.splitext(path_input)[1] == '.py':
            check_for_err(path_input)
    else:
        paths = os.listdir(path_input)
        for p in paths:
            if p == 'tests.py':
                continue
            p = os.path.join(path_input, p)
            if os.path.splitext(p)[1] == '.py':
                check_for_err(p)
