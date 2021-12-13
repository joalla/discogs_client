# Contribution

There are several ways you can help improve the `python3-discogs-client` library.

- Help others in the [support section of our github repo](
  https://github.com/joalla/discogs_client/discussions/categories/support).
- [Improve the documentation](
  https://github.com/joalla/discogs_client/tree/master/docs).
- [Suggest and discuss fixes and features](
  https://github.com/joalla/discogs_client/discussions/categories/ideas).
- [Submit your fixes and features](#submitting).
- [Chat with others](
  https://github.com/joalla/discogs_client/discussions/categories/projects)
  about projects and collaborate around the Client.


## Submitting

Submit changes to the code or the documentation by forking our repo and submitting a pull-request to the master branch. If you are unsure about anything or have questions, please [add a post in in the Ideas section](https://github.com/joalla/discogs_client/discussions/categories/ideas) of Discussions.

first get in contact in the ideas section on the discussion board.


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
