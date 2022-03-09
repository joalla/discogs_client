# Writing and Updating Documentation

## Fork and Clone the Repository

The first step is to fork the repository.  In the upper right hand corner of Github, click the ```Fork``` button.  This will create a copy of the repository in your account.

The second step is to clone the ```python3-discogs-client``` library to your computer.  From the ```python3-discogs-client``` fork you just created, press the ```Code``` button, copy the ```git``` URL and clone it in your code editor of choice, or use the terminal:

```
git clone <git url>
```

## Install Prerequisites

Install Sphinx

```
pip install -r sphinx_requirements.txt
```

Install python3-discogs-client itself into your (virtual) development environment. This is required by Sphinx autodoc:

```
python setup.py develop
```

## Edit Files

Create a new branch in git and start editing the documentation:

```
git checkout -b my_docs_changes_branch
```

Documentation files are in the ```docs/source``` directory. You can edit the files in this directory to add or update content.

Almost all documentation is written using the Markdown format.  The exception is the ```index.rst``` page, which is written in reStructuredText format.  If you are adding a new page or pages, please add them to the menu structure in reStructuredText format in the ```index.rst``` page.

## Build the Documentation

After your changes are complete, you can build the documentation by running the ```make html``` command.  This will build the documentation in the ```docs/build/html``` directory.  

Please note that as of this writing, Python 3.10 will not work.  Please use Python Python >=3.6 and <=3.9 when building the documentation.

Check the command line input to make sure no errors occurred.  If there is an error, fix it, and re-run the command. You can ignore warnings similar to this one:

`docstring of discogs_client.models.Artist.id:10: WARNING: Unexpected indentation.`

Open `docs/build/html/index.html` in your web browser to review the changes.  After you are satisfied with the changes, commit them to your local repository and push to your fork.

For some changes it's necessary to clean up before build:

```
make clean; make html
```

## Create a Pull Request

To create a pull request, please [read Github's documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) on forking and creating pull requests.