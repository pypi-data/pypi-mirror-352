# rs-template

This is a template repo demonstrating best practices. You can make your own repo from this template, which should save you a lot of work! Just be sure to find-and-replace for "rs-template", "rs_template", and "dennisbrookner" and update everything.

This file is a guide to the core elements that your project should have. In some cases, you may opt for a reasonable alternative, but all of this core functionality should be present.

## General organization

The following files in this repo should be adapated for your repo:

### [`pyproject.toml`](/pyproject.toml) configuration file
This is the configuration file for the package. The example in this repo is a good starting point. Some things to note:
 - I recommend using the `[build-system]` and `[tool.hatch.version]` blocks exactly, and including `dynamic = ["version"]` in the `[project]` block. This allows you to version your package through numbered "releases" on GitHub. There are other ways to do this, but I think this is the best one.
 - There are three different types of dependencies in this file. First, the core `dependencies = ` in the `[project]` block are python packages which are required for your package to function. The `[project.optional-dependencies]` block adds two more types of dependencies:
     - `test`: Any packages necessary to run the test suite.
     - `docs`: Any packages necessary to build the package documentation. More on this below.

The contents of the `pyproject.toml` file are described in more detail [here](https://packaging.python.org/en/latest/flow/#the-configuration-file)

### [`setup.py`](/setup.py) legacy file
Using `setup.py` to define package configuration and installation is deprecated. However, for legacy reasons, the `setup.py` file must exist. You can adapt the example in this repo.

### [`LICENSE`](/LICENSE)
Pick an open-source license to use, or copy the one here (MIT license).

### [`tox.ini`](/tox.ini)
Adapt this file. This file defines configurations for GitHub actions that will be run.

### [`.pre-commit-config.yaml`](/.pre-commit-config.yaml)
Copy this file exactly, or change it if you'd like. This file will configure the "pre-commit" checks which can enforce code formatting and other similar things.

### [`.gitignore`](/.gitignore)
Cookie-cutter python gitignore file.

## Code
The actual code for your package lives in the `/src/{package-name}` directory. This folder **must** contain an `__init__.py` file, even if it is empty. Ideally, use the `__init__.py` file to define what can be imported from your package.

See the [python documentation](https://packaging.python.org/en/latest/) for more details on code organization.

### Code for command-line utilities
Command-line utilities should be structured such that the utility can be called by calling some function, likely the `main` function. Then, you can add the following to your `pyproject.toml` to give this utility a name and make it available from the command line:

```toml
[project.scripts]
"rs.template" = "rs_template._command_line:main"
```

## Docs
The `/docs` folder contains the necessary files to build package documentation. The files `make.bat` and `Makefile` are entirely cookie-cutter and can be copied exactly.

### `conf.py` configuration file for docs
There are lots of fun options here, but I recommend the sensible defaults in the example file. For more information, check out the [sphinx documentation](https://www.sphinx-doc.org/en/master/).

Note that if your documentation is to include a python API reference, you must include `"sphinx.ext.autodoc"` in `extensions = `. If your documentation is to include a command-line API reference, you must include `"sphinxcontrib.autoprogram"`.

If you want your documentation to include rendered jupyter notebooks, you can find code for this in various commented-out options in this file.

Note that the [`"myst_parser"`](https://myst-parser.readthedocs.io/en/latest/) extension allows pages to be written in a blend of markdown and reStructuredText. There are examples of this throughout the documentation.

### `index.md`: Your homepage
All websites need a homepage! This file can be written in markdown, and will be rendered into HTML based on the theme that you've picked. The only essential non-markdown element is the table of contents; see the `/docs/index.md` file in this repo for an example of the syntax.

### Other pages
You can add more pages to your documentation by just adding more `.md` files to the `/docs/` directory. You'll probably want to add any pages to your site's table of contents, which lives at the bottom of `index.md`. These files can include whatever you want! You can add images if you want; just stick the images into the `/docs/images/` directory, and use markdown syntax.

The files `/docs/api.md` and `/docs/cli.md` contain examples of how to automatically render documentation for a python API or a command-line API. As mentioned above, using something like this will add the `"sphinx.ext.autodoc"` or `"sphinxcontrib.autoprogram"` dependencies to your site. For real examples of usage with a more complicated API, see [reciprocalspaceship](https://github.com/rs-station/reciprocalspaceship/blob/main/docs/api/index.rst) for python API or [matchmaps](https://github.com/rs-station/matchmaps/blob/main/docs/cli.md) for CLI

### Building docs locally
Building docs right from your computer is easy!

 1. Install your package, including the `[docs]` dependencies. Do this by navigating into the package directory and calling `pip install -e ".[docs]"`
 2. Navigate into the `/docs` directory and call `make html`. This will build the package documentation and place it in the `/docs/_build` directory.
    - Note that when repeatedly building documentation, you should call `make clean` each time, followed by `make html`.
 3. Open the file `/docs/_build/html/index.html` in your browser. This is your site! Links to other pages in the site should all work, so you can explore the documentation here.

## Tests
This template repo just has a placeholder test function. Check out [reciprocalspaceship](https://github.com/rs-station/reciprocalspaceship/tree/main/tests) for a good example of what more fleshed-out tests should look like.

## Workflows
You package should contain (at least) these workflows, which live either in the [`.github`](/.github) folder or in the [`.github/workflows`](/.github/workflows/) subfolder.

### [`ci.yml`](/.github/workflows/ci.yml)

CI stands for "continuous integration". This is the workflow that actually builds your python package. Any time there is either a push or a pull to the main branch of your repo, this workflow will run and build your package.

Additionally, when you create a new version of your package (by making a new release) this workflow is responsible for deploying your latest version to PyPI.

### [`build_docs.yml`](/.github/workflows/build_docs.yml)

This workflow will build your package's documentation and deploy it online. This will be run any time that there is a push to the main branch of your repo. Note that this means that the online documentation may be "ahead" of the package version found on PyPI.

### [`test_docs.yml`](/.github/workflows/test_docs.yml)

This workflow is run on *pull requests* to the main branch. It builds your documentation, but does not deploy it online. This ensures that any changes made in your PR do not break the documentation.

### [`cron.yml`](/.github/workflows/cron.yml)

This workflow ensures that your package has not been broken by any unexpected changes to dependencies. You can configure it to run on a schedule. The `tox.ini` file defines what is tested by this workflow.

### [dependabot](/.github/dependabot.yml)

[Dependabot](https://github.com/dependabot) is a GitHub tool to help make sure your GitHub workflows and actions and such are up-to-date. This file enables dependabot for the repository.

### [Failure template](/.github/TEST_FAIL_TEMPLATE.md)

This file is just a necessary complement to `tox.ini`, allowing GitHub to create an issue in the repository if tox fails.

## Essential Git / GitHub tasks

Some final chores that you'll need to do to get your package up and running. Some of these are things that you'll need to do online, even after creating this repo as described above. They can be a little tricky, but I'll describe them here as best I can!

### Creating an "orphan" `gh-pages` branch

The architechture described here allows GitHub to build your documentation and then deploy it to the `gh-pages` branch. For this to work, you want to make a branch for your repo called `gh-pages` which is an "orphan", e.g., it just lives in its own world and does not track changes with any other branches.

The easiest way to do this is from the command line. Just be careful! Make sure that you have successfully switched to your `gh-pages` branch before you `git rm` everything.

```bash
# make the orphan branch
git checkout --orphan gh-pages

# preview files to be deleted from git
git rm -rf --dry-run .
# actually delete the files from git
git rm -rf .

# make an empty index.html
touch index.html
git add index.html
git commit -m "initial commit to gh-pages branch"

# push the gh-pages branch online
git push origin gh-pages

# get back to the main branch
git checkout main
```

You then have to tell GitHub about this change. In settings, you want to choose "deploy from a branch" as your source, and deploy from gh-pages, root directory. It should look like this:

![Screenshot of github settings](/docs/images/ghpages_settings.png)

Now GitHub will look at the `gh-pages` branch and send whatever is there to rs-station.github.io/{your-repo}. You should be able to run your `build_docs` workflow, and your content will end up on the internet!

#### Don't forget the `.nojekyll` file

In a silly turn of events, all of the style information for the website lives in a folder with a leading underscore, and by default, GitHub *ignores* directories with leading underscores. You override this behavior by creating an empty file on the `gh-pages` branch called `.nojekyll`. (It's possible you could have done this above when you were creating things from the command-line, but I'm not sure.)

### PyPI

At this point, your package should be `pip`-installable via the `git+` syntax, e.g.:
```bash
pip install git+https://github.com/rs-station/rs-template.git
```
but your goal is probably to put your package on [PyPI](https://pypi.org/), such that it can be `pip`-installed directly.

The process of sending a package to PyPI is described [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/). I recommend following this tutorial, including sending your package to TestPyPI as a test. If you're already up to this point, you might be able to skip down to ["Generating distrubution archives"](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives) in the tutorial.

#### Dynamic versioning workaround

One issue you will run into is that PyPI does *not* support dynamic version names like `rs_template-0.1.dev9+g3ae71f2`. As a quick workaround, I recommend briefly switching to static versioning, e.g. by editing your `pyproject.toml` to look like:

```toml
# dynamic = ["version"]
version='0.0.1'
```
With the version temporarily pinned to `0.0.1`, you should be able to run `twine upload` successfully. After this, you can switch back to dynamic versioning.

#### Re-using your API key for GitHub actions

When you make an API key for PyPI, you'll need this key twice. First, you'll have to provide it in the command-line when you first upload your package. Then, you'll also need to provide this key to GitHub, so that GitHub can upload the package to PyPI on your behalf:
![Github token settings](/docs/images/github_pypi_secret.png)

Note that this key is different from your API key for TestPyPI!

Both of these API keys should be stored in a safe place, because you might want them again if you're making another package!

## Living your best developer life
Once this is all set up, development should be a breeze!

You can make more branches of your repo when you want to make changes to code. Any time you create or merge a pull request back to the main branch, these workflows will keep all your code running smoothly and alert you to any errors.

Don't forget that in order to push your changes to PyPI, you'll need to create a "Release" and tag on GitHub. You can inform users that if they want to get the latest changes that haven't made it to PyPI yet, they can install the development version of the package using the `pip install git+` syntax.
