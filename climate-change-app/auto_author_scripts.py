"""
Author: Tom
"""

import os
import subprocess

include_extensions = ['py', 'html']
exclude_patterns = ['auto_author_scripts.py', 'venv\\', '__init__.py', 'reports\\']

project_files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(".")) for f in fn]

project_files = [file for file in project_files if any(file.endswith(ext) for ext in include_extensions)]

for file in project_files:
    if any(exclude_pattern in file for exclude_pattern in exclude_patterns):
        continue

    with open(file, 'r') as f:
        content = f.read()

    if file.endswith('py'):
        if content.strip().startswith('"""'):
            print(f'Skipping {file}')
            continue

    if file.endswith('html'):
        if content.strip().startswith('{#'):
            print(f'Skipping {file}')
            continue

    print(f'Authoring {file}')

    command = "git shortlog -sn " + file
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    authors = stdout.decode('utf-8').split('\n')
    authors = [author.split('\t')[1].strip() for author in authors if author != '']

    name_map = {
        'Adam': 'Adam'
    }

    mapped_authors = set()

    for author in authors:
        if author in name_map:
            mapped_authors.add(name_map[author])
        else:
            print(f'Unknown author: {author}')

    authors_string = ', '.join(mapped_authors)
    if file.endswith('py'):
        docstring = f'''"""
Author: {authors_string}
"""

'''

    if file.endswith('html'):
        docstring = f'''{{#
    Author: {authors_string}
#}}

'''

    with open(file, 'w') as f:
        f.write(docstring + content)
