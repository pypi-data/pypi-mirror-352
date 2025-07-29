# TinyROS
A minimal Robotic Operating System for GPU-first robots.

Features:
- .... I will finish this README soon

## Installation
```bash
pip install tinyros
```

## Example
Soon. You can check out the tests for now, in particular test_architect.py

## Why TinyROS?
You know it :D

## Questions
Please open a separate GitHub issue for each question or requested feature.

## Citation
If you use `TinyROS` in your research (you should, drop ROS/ROS2!!!), please hand out a citation:
```bibtex
@software{terpin2025tinyros,
  author       = {Terpin, Antonio},
  title        = {{TinyROS}: A Lightweight Robot Operating System for GPU-first robots},
  year         = {2025},
  version      = {1.0.0},
  url          = {https://github.com/atrepin/tinyros},
}
```

## Contributing
The `Coding style validation` action will fail if the pre-commit checks do not pass. To make sure that these are checked automatically on push, run:
```sh
pre-commit install --hook-type pre-push --install-hooks
```
To run the pre-commit checks on specific files:
```bash
pre-commit run --files <files>
```
To run on all files:
```bash
pre-commit run --all-files
```
If for some reason you really want to ignore them during commit/push, add `--no-verify`.

To ease writing commit messages that conform to the [standard](https://www.conventionalcommits.org/en/v1.0.0/#summary), you can configure the template with:
```bash
git config commit.template .gitmessage
```
To fill in the template, run
```bash
git commit
```
When you have edited the commit, press `Esc` and then type `:wq` to save. In `Visual Studio Code`, you should setup the editor with
```bash
git config core.editor "code --wait"
```
You may need to [setup the `code` command](https://code.visualstudio.com/docs/setup/mac).
The `Commit style validation` action will fail if you do not adhere to the recommended style.

Tip: When something fails, fix the issue and use:
```bash
git commit --amend
git push --force
```

### Development workflow
We follow a [Git feature branch](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) workflow with test-driven-development. In particular:

- The basic workflow is as follows:
  1. Open an issue for the feature to implement, and describe in detail the goal of the feature. Describe the tests that should pass for the feature to be considered implemented.
  2. Open a branch from `dev` for the feature:
    ```bash
    git checkout dev
    git checkout -b feature-<issue-number>
    ```
  3. Add the tests; see [Testing](#testing-a-feature).
  4. Implement the feature and make sure the tests pass.
  5. Open a PR to the `dev` branch. Note that the PR requires to `squash` the commit. See [Preparing for a PR](#preparing-for-a-pr).
  6. Close the branch.

- `main` and `dev` branches are protected from push, and require a PR.
- We run github actions to check the test status on push on any branch. The rationale is that we want to know the state of each feature without polling the developer.
- We open a PR to `main` only for milestones.

### Testing a feature
We will use [pytest](https://docs.pytest.org/en/stable/) to thoroughly test all our code. To run all tests:
```bash
pytest -v
```
Before pushing a feature, implement also the related test. The goal is to make sure that if something does not behave as expected (possibly as a result of another change) the tests capture it.


### Preparing for a PR
Before opening a PR to `dev`, you need to `squash` your commits into a single one. First, review your commit history to identify how many commits need to be squashed:
```bash
git log --oneline
```
For example, you may get
```bash
abc123 Feature added A
def456 Fix for bug in feature A
ghi789 Update documentation for feature A
```
Suppose you want to squash the three above into a single commit, `Implement feature <issue-number>`. You can rebase interactively to squash the commits:
```bash
git rebase -i HEAD~<number-of-commits>
```
For example, if you want to squash the last 3 commits:
```bash
git rebase -i HEAD~3
```
An editor will open, showing a list of commits:
```bash
pick abc123 Feature added A
pick def456 Fix for bug in feature A
pick ghi789 Update documentation for feature A
```
- Keep the first commit as `pick`.
- Change `pick` to `squash` (or `s`) for the subsequent commits:
```bash
pick abc123 Feature added A
squash def456 Fix for bug in feature A
squash ghi789 Update documentation for feature A
```
Save and close the editor.
Git will prompt you to edit the combined commit message. You’ll see:
```bash
# This is a combination of 3 commits.
# The first commit's message is:
Feature added A

# The following commit messages will also be included:
Fix for bug in feature A
Update documentation for feature A
```
Edit it into a single meaningful message, like:
```bash
Add feature A with bug fixes and documentation updates
```
Save and close the editor; Git will squash the commits. If there are conflicts during the rebase, resolve them and continue:
```bash
git rebase --continue
```
Verify the commit history:
```bash
git log --oneline
```
You should see one clean commit instead of multiple. If you’ve already pushed the branch to a remote repository, you need to force-push after squashing:
```bash
git push --force
```
Now that the feature branch has a clean history, create the PR from your feature branch to the main branch. The reviewers will see a single, concise commit summarizing your changes. See the [guidelines for commit messages](https://www.conventionalcommits.org/en/v1.0.0/#summary).
