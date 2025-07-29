# How this Template was Made

## Initialise Repo and Environment

1. **Created a new repository on [GitHub](https://github.com/).**
      - Gave an appropriate name and description.
      - Added a README file.
      - Added a .gitignore file for Python.
      - Selected a license (MIT License).

    ![Github Repo](./images/github_create_repo.png)

1. **Added [Copilot Context File](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)**
      - Created a [`.github/copilot-instructions.md`](https://github.com/hungovercoders/template.python.package/blob/main/.github/copilot-instructions.md){target="_blank"} file to provide context for Copilot.

1. **Opened in codespaces and amended environment configuration.**
      - Added a [`devcontainer.json`](https://github.com/hungovercoders/template.python.package/blob/main/.devcontainer/devcontainer.json){target="_blank"} file to configure the development environment using [devcontainers](https://code.visualstudio.com/docs/remote/devcontainer){target="_blank"} standards in [vs code](https://code.visualstudio.com/docs/devcontainers/containers){target="_blank"}.
      - Added a [requirements_dev.txt](https://github.com/hungovercoders/template.python.package/blob/main/.devcontainer/requirements_dev.txt){target="_blank"} file for the packages required for development.
      - Added a [requirements_docs.txt](https://github.com/hungovercoders/template.python.package/blob/main/.devcontainer/requirements_docs.txt){target="_blank"} file for the packages required for documentation.
      - Created a [setup.sh](https://github.com/hungovercoders/template.python.package/blob/main/.devcontainer/setup.sh){target="_blank"} file to automate the post create setup process in the devcontainer.

1. **Reopened the codespace to confirm devcontainer configuration**
    - Confirmed VS code extensions installed.
    - Leveraged errorlens and spell checker to clean-up any markdown or spelling errors.

    ![Error Lens and Spell Checker](./images/errorlens_spellcheck.PNG)

    - Confirmed package requirements installed in the codespace.
  
    ```bash
    pip list
    ```

    ![Pip List](./images/pip_list.PNG)

## Published Documentation

1. **Created documentation**
      - Utilising [MkDocs](https://www.mkdocs.org/){target="_blank"} for documentation generation, installed as part of devcontainer setup.
      - Created a [`mkdocs.yml`](https://github.com/hungovercoders/template.python.package/blob/main/mkdocs.yml){target="_blank"} file to configure the documentation.
      - Created a `docs` directory with an initial [`index.md`](https://github.com/hungovercoders/template.python.package/blob/main/docs/index.md){target="_blank"} file.
      - Built the documentation using:

      ```bash
      mkdocs build --strict
      ```

      - Served the documentation locally to confirm it works:

      ```bash
      mkdocs serve --strict
      ```

      ![Local Documentation Served](./images/local_mkdocs.PNG)

2. **Published documentation to GitHub Pages**
      - Enabled GitHub Pages in the repository settings, selecting the `gh-pages` branch as the source.

      ![Github Pages Configuration](./images/github_pages.PNG)

      - Created a `.github/workflows/gh-pages.yml` file with the necessary steps to build and deploy the documentation to the github pages branch configured above.
      - Committed and pushed changes to trigger the workflows.
      - Confirmed the documentation is available at `https://<username>.github.io/<repository-name>/`. e.g. [https://hungovercoders.github.io/template.python.package/](https://hungovercoders.github.io/template.python.package/){target="_blank"}

      ![Published Docs](./images/published_docs.PNG)

## Created Changelog

1. **Create a [`docs/changelog.md`](https://github.com/hungovercoders/template.python.package/blob/main/docs/changelog.md){target="_blank"} file**
      - Utilised [git-cliff](https://github.com/git-cliff){target="_blank"} for changelog generation installed as part of devcontainer setup.
      - Created a cliff.toml file to configure the changelog.
      - Confirmed working by running:

      ```bash
      git-cliff -c cliff.toml
      ```

      - Can see changelog file populated locally.

      ![Local Change Log](./images/change_log_local.PNG)

2. **Added a GitHub Action to automatically generate the changelog**
      - Amended [`.github/workflows/gh-pages.yml`](https://github.com/hungovercoders/template.python.package/blob/main/.github/workflows/gh-pages.yml){target="_blank"} file to include a step to generate the changelog automatically using git-cliff.
      - Confirmed working by pushing changes and checking the generated changelog on live documentation site.

      ![Published Change Log](./images/change_log_published.PNG)

## Initialise Package

1. **Initialised the package using [uv](https://github.com/ultraq/uv)**

      - Leveraged [uv](https://docs.astral.sh/uv/){target="_blank"} to initialise the package which was installed as part of devcontainer setup.
      - Execute script below to initialise package.
  
      ```bash
      uv init --lib hungovercoders_template_python_package
      ```

      - Moved pyproject.toml and python-version file along with src folder to the root of the repo and cleared up directory.
      - Added [`greetings`](https://github.com/hungovercoders/template.python.package/blob/main/src/hungovercoders_template_python_package/greetings.py){target="_blank"} module with hello function with the ability to call cli.
      - Updated [pyproject.toml](https://github.com/hungovercoders/template.python.package/blob/main/pyproject.toml){target="_blank"} file with appropriate configuration details including a cli call to the hello function.
      - Installed the package locally using:

      ```bash
      pip install -e .
      ```

      - Confirmed the package is installed and working by running:

      ```bash
      hungovercoders-template-hello --name griff
      ```

      - Output should be:

      ```
      Hungovercoders say hello to griff!
      ```

1. **Added tests for the package**
      - Created a [`tests`] directory with an initial [`test_greetings.py`](https://github.com/hungovercoders/template.python.package/blob/main/tests/test_greetings.py){target="_blank"} file.
      - Utilised [pytest](https://docs.pytest.org/en/stable/){target="_blank"} for testing, installed as part of devcontainer setup by running: 
  
      ```bash
      pytest
      ```
      - Confirmed tests pass and package is functioning as expected.
      ![Pytest Output](./images/pytest_output.PNG)

1. **Linted the code**
      - Utilised [ruff](https://github.com/charliermarsh/ruff){target="_blank"} for linting, installed as part of devcontainer setup.

      - Confirmed code is linted and follows best practices by running the command.

      ```bash
      uvx ruff check .
      ```

1. **Checked distribution files**
      - Utilised [twine](https://twine.readthedocs.io/en/stable/){target="_blank"} to check the distribution files.
      - Created the distribution files using:

      ```bash
      uv build
      ```

      - Checked the distribution files using:

      ```bash
      uvx twine check dist/*
      ```

1. **Created github actions to run linting, distribution and testing on pull requests and pushes to main branch.**
      - Created a [`.github/workflows/ci.yml`](https://github.com/hungovercoders/template.python.package/blob/main/.github/workflows/ci.yml){target="_blank"} file with the necessary steps to run linting, distribution checks and testing.
      - Confirmed working by pushing changes and checking the actions tab in GitHub.
      - Test results can be seen to be published correctly.
         ![CI Output](./images/ci_output.PNG)


## Publish Package to PyPI

1. **Created a PyPI account**
      - Created an account on [PyPI](https://pypi.org/account/register/){target="_blank"}.
      - Created an API token for the account.
      - Added the PyPI credentials to the GitHub repository secrets as `PYPI_API_TOKEN`.

1. **Amended the CI workflow**
      - Amended the [`.github/workflows/ci.yml`](https://github.com/hungovercoders/template.python.package/blob/main/.github/workflows/ci.yml){target="_blank"} file to include a step to publish the package to PyPI if a new tag is pushed.

1. **Create tag and push script**
      - Created a [`tag_and_push.sh`](https://github.com/hungovercoders/template.python.package/blob/main/scripts/tag_and_push.sh){target="_blank"} script to create a new tag and push it to the remote repository.

1. **Pypi confirmation**
      - Confirmed the package is available on PyPI by visiting [https://pypi.org/project/hungovercoders-template-python-package/](https://pypi.org/project/hungovercoders-template-python-package/){target="_blank"}.
      - Confirmed the package can be installed using:

      ```bash
      pip install hungovercoders-template-python-package
      ```

      - Confirmed the package is working by running:

      ```bash
      hungovercoders-template-hello --name griff
      ```

      - Output should be:

      ```
      Hungovercoders say hello to griff!
      ```

## Added Schema Validation

```bash
hungovercoders-validate-organisation /workspaces/template.python.package/tests/examples/organisation.json 
```

```bash
hungovercoders-validate-organisation /workspaces/template.python.package/tests/examples/organisation.json --output-format json
```

```bash
hungovercoders-validate-organisation --show-schema
```