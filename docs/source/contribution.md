# Contribution

There is several ways you can help improve python3-discogs-client.

- Help others in the [support section of our github repo](
  https://github.com/joalla/discogs_client/discussions/categories/support).
- [Improve the documentation](
  https://github.com/joalla/discogs_client/tree/master/docs).
- [Suggest and discuss fixes and features](
  https://github.com/joalla/discogs_client/discussions/categories/ideas).
- [Submit your fixes and features](#submitting).
- [Chat with others](
  https://github.com/joalla/discogs_client/discussions/categories/projects)
  about projects and collaboration around the Client.


## Submitting

Submit changes to the code or the documentation by forking our repo and submitting a pull-request to the master branch. If you are unsure about anything, first get in contact in the ideas section on the discussion board.


## Test an unreleased feature

Sometimes you'd want to use or test a feature that is not yet released, one reason being a pull request is not merged yet.

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
