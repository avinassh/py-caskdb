# Contribution Guidelines

I am happy to accept PRs on CaskDB. For short bug/typo fixes, feel free to open a PR directly. 

I accept PRs related to the challenges mentioned in the different levels. Please open a separate PR for each challenge. The shorter PR is better. It is easier to review and catch bugs.

For any new feature (or the level challenges) in the db, please open a GitHub issue and discuss your design/changes first.

Do *NOT* club multiple things into a single PR. This adds unnecessary work for me, and it will take way longer for me to review. 
- CaskDB is an educational project. PRs become a great learning point for someone new to navigate the codebase and add a new feature.
- Your PRs will be a great stepping stone for someone else who is new.

Thank you!

## Branches

- `start-here` contains all the base challenges and test cases
- `master` implements the base challenges
- `final` implements challenges from different levels

If your PR is a bug/typo fix, open a PR with `master` as the base. I will backport the changes to `start-here` and `final` once merged.

If you are implementing something new, open a PR with `final` as the base.

## "I am new; how do I get started?"

Pick any challenge from any level and open a GitHub issue to discuss. I am happy to provide more resources/research papers to understand a particular concept.
