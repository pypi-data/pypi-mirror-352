# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autopr']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub==2.6.1',
 'PyYAML==6.0.1',
 'click==8.1.7',
 'marshmallow-dataclass==8.6.1',
 'marshmallow==3.21.3',
 'single-source==0.4.0']

entry_points = \
{'console_scripts': ['auto-pr = autopr:main']}

setup_kwargs = {
    'name': 'auto-pr',
    'version': '1.0.10',
    'description': 'Perform bulk updates across repositories',
    'long_description': '<img width="128" src="https://github.com/getyourguide/auto-pr/raw/master/img/logo.svg" alt="auto-pr logo" />\n\n![CI](https://github.com/getyourguide/auto-pr/workflows/CI/badge.svg)\n[![Publish](https://github.com/getyourguide/auto-pr/actions/workflows/publish.yml/badge.svg)](https://github.com/getyourguide/auto-pr/actions/workflows/publish.yml)\n[![PyPI version](https://badge.fury.io/py/auto-pr.svg)](https://badge.fury.io/py/auto-pr)\n![PyPI downloads](https://img.shields.io/pypi/dm/auto-pr)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# auto-pr\n\nA command line tool to perform bulk updates across multiple GitHub repositories.\n\n## How to install\n\nWith [pipx](https://pipxproject.github.io/pipx/) (recommended):\n\n```bash\npipx install auto-pr\n```\nWith pip:\n\n```bash\npip install auto-pr\n```\n\n## Usage\n\n[![Usage](https://github.com/getyourguide/auto-pr/raw/master/img/workflow.svg)](https://github.com/getyourguide/auto-pr/raw/master/img/workflow.svg)\n\n### Init\n\nFirst initialise the project directory by running the `init` command within an empty directory.\n\n```bash\nauto-pr init --api-key=<github_token> --ssh-key-file=<path-to-ssh-key>\n```\n\nWhere `<github_token>` is a GitHub [personal access token](https://github.com/settings/tokens) which has `repo` and `user:user:email` scope.\n\nNext modify the generated `config.yaml` file with your desired configurations.\n\n```yaml\ncredentials:\n  api_key: <github_token>\n  ssh_key_file: /path/to/ssh/key/to/push/.ssh/id_rsa\npr:\n  body: >\n    Body of the PR that will be generated\n\n    Can be multi-line :)\n  branch: auto-pr # The branch name to use when making changes\n  message: Replace default pipelines with modules # Commit message\n  title: \'My awesome change\' # Title of the PR\nrepositories: # Rules that define what repos to update\n  - mode: add\n    match_owner: <org/user>\nupdate_command:\n  - touch\n  - my-file\n```\n\nIf you wish to keep your API Key outside of `config.yaml`, set the env var `APR_API_KEY` with your GitHub Token\n\n### Repositories\n\nYou can define the list of repositories to pull and build into the database to update using a list of rules.\n\n-   `mode` - either `add` or `remove` - used to either match or negate\n-   `public` (optional) - pull only public or private, leave out for both\n-   `archived` (optional) -  archived or non-archived, leave out for both\n-   `match_owner` (optional) - the owner or user to pull\n-   `match_name` (optional) - a list of regular expressions to match against to pull\n\nThe flags of the filter rules are optional not specifying will run the command on all repositories that the token has access too.\n\n### Update Command\n\nThis is the list containing the command to be executed along with the arguments passed to it. It will be executed from\nthe root of each repository that is processed.\n\nIf an error occurs during the execution it will be displayed in the output but will not halt the execution.\n\nSee [example commands](docs/examples.md#commands)\n\n### Pull\n\nAfter you have configured the project you can now pull the repositories down that match your rules.\n\n```bash\nauto-pr pull\n```\n\nThis will generate a `db.json` file within your workdir containing a list of mapped repositories and their state.\n\nThis command can be run multiple times, if there are new matching repositories found they will be merged into the existing database.\n\nIf you would like to use your globally set config, you can pass the option `--use-global-git-config` when pulling the repos. If you had already pulled the repos before this and you would like to change the config for those repos, you would also need to pass `--update-repos` alongside the global-git-config option when pulling.\n\n### Test\n\nOnce the `pull` command has finished setting up the work directory you can now run test to check what the changes that will be made by the script will yield.\n\n### Run\n\nWhen you\'re confident with the changes output from the `test` command you can finally execute `run`.\n\n```bash\nauto-pr run\n```\n\nThis will perform the changes to a branch on the locally cloned repository and push the branch upstream with the information you provided within `config.yaml`.\n\nBy default, the commits will be associated with your primary email and name, which were set on the repo level for those repos when you ran `auto-pr pull`. If you would like to use your global git config for the repos that you already pulled, you need to run pull again with:\n\n```\nauto-pr pull --update-repos --use-global-git-config\n```\n\nSee `--help` for more information about other commands and their  usage.\n\n### Reset\nYou can reset the list of repos in `db.json` using `auto-pr reset all`, or `auto-pr reset from FILE`\n\nWhen using `auto-pr reset from FILE`, the list of repos should be provided as a newline separated list of repos like `<owner>/<name>`, e.g:\n\n```text\ngetyourguide/test\ngetyourguide/auto-pr\n```\n\n## Security\n\nFor sensitive security matters please contact [security@getyourguide.com](mailto:security@getyourguide.com).\n\n## Legal\n\nCopyright 2021 GetYourGuide GmbH.\n\nauto-pr is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.\n',
    'author': 'GetYourGuide GmbH',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/getyourguide/auto-pr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
