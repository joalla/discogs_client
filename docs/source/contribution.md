# Contribution

There are several ways you can help improve the `python3-discogs-client` library.

- Help others in the [support section of our github repo](
  https://github.com/joalla/discogs_client/discussions/categories/support).
- [Improve the documentation](##Writing Documentation).
- [Suggest and discuss fixes and features](
  https://github.com/joalla/discogs_client/discussions/categories/ideas).
- [Submit your fixes and features](#submitting).
- [Chat with others](
  https://github.com/joalla/discogs_client/discussions/categories/projects)
  about projects and collaborate around the Client.


## Submitting

Submit changes to the code or the documentation by forking our repo and submitting a pull-request to the master branch. If you are unsure about anything or have questions, please [add a post in in the Ideas section](https://github.com/joalla/discogs_client/discussions/categories/ideas) of Discussions.

## Test an unreleased feature

Sometimes you might want to use or test a feature that has not been released yet, such as a pull request that needs to be tested.

You can install from a development branch like this:

```
pip install -e git+https://github.com/pr_submitters_user_name/discogs_client@feature_branch_name#egg=python3-discogs-client
```

Or temporarily write this into your requirements.txt:

```
-e git+https://github.com/pr_submitters_user_name/discogs_client@feature_branch_name#egg=python3-discogs-client
```

And then re-install all the dependent packages using the file as the input
source:
```
pip install -r requirements.txt --update
```

## Writing Documentation

You can help keep the documentation current by editing or adding new pages to the documentation.  Please see the [Writing Documentation page](writing_docs.md) for more information on how to clone the repository, edit the documentation, and build the documentation.
