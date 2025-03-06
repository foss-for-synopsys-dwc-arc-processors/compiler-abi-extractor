# Contributing Guide

* [New Contributor Guide](#contributing-guide)
  * [Ways to Contribute](#ways-to-contribute)
  * [Find an Issue](#find-an-issue)
  * [Ask for Help](#ask-for-help)
  * [Pull Request Lifecycle](#pull-request-lifecycle)
  * [Development Environment Setup](#development-environment-setup)
  * [Reference Reports](#reference-reports)
  * [Sign Your Commits](#sign-your-commits)

Welcome! We are glad that you want to contribute to our project! 💖

As you get started, you are in the best position to give us feedback on areas of
our project that we need help with including:

* Problems found during setting up a new developer environment
* Gaps in our Quickstart Guide or documentation
* Bugs in our automation scripts

If anything doesn't make sense, or doesn't work when you run it, please open a
bug report and let us know!

## Ways to Contribute

We welcome many different types of contributions including:

* New features
* Bug fixes
* Documentation
* Issue Triage

## Find an Issue

To ask for an issue to work on, contributors can follow these steps:

1. **Browse Open Issues** \
   Start by looking through the list of [open issues](https://github.com/foss-for-synopsys-dwc-arc-processors/compiler-abi-extractor/issues) in the repository to find tasks or bugs that are of interest.

2. **Check for Labels** \
   Look for issues labeled with `good first issue` or similar tags indicating tasks suitable for new contributors. These issues are often simpler and a good starting point.

3. **Comment on the Issue** \
   Once you find an issue you'd like to work on, leave a comment on that issue expressing your interest. Let the maintainers know you’d like to take it on. If no one else is assigned to the issue, they may assign it to you.

4. **Wait for Confirmation** \
   After expressing interest, wait for a confirmation from the maintainer. This ensures that the issue is available and ready for you to start working on.

5. **Start Working** \
   Once confirmed, begin working on the issue according any instructions provided in the issue description.

6. **Submit a Pull Request** \
   When your work is complete, submit a pull request with your changes and reference the issue in your PR description. This will help maintainers track progress and review your work.


## Ask for Help

The best way to ask questions is by [creating a new issue](https://github.com/foss-for-synopsys-dwc-arc-processors/compiler-abi-extractor/issues/new?template=Blank+issue) or by commenting on an existing related issue.

## Pull Request Lifecycle

Contributors are encouraged to submit a pull request (PR) when their work is ready for review. If early feedback is needed, a draft PR can be opened to indicate that the work is still in progress. When a PR is ready for review, it should be converted to a regular PR and include a clear description of its purpose and any remaining considerations.

Reviews are typically provided within a few days of submission. Once feedback is addressed, follow-up reviews are usually quicker. If a PR appears stalled, contributors can comment on it to request further review. If there is still no response after a reasonable period, mentioning a maintainer may help move things forward. For PRs that remain stuck without feedback, discussing the issue separately may be a good alternative.

Smaller, incremental PRs are preferred over large, feature-complete submissions. Breaking down major changes into multiple smaller PRs makes the review process more efficient and increases the chances of timely approval. For significant changes, using feature branches is recommended to keep development organized.

If a contributor no longer wants to continue with a PR, they should either close it or inform the maintainers. In some cases, maintainers may push minor fixes directly to a PR to help it get merged. If a PR remains inactive for an extended period without a response, it may be closed.

Once a PR is merged, it will be included in the next release according to the project’s release schedule. Urgent fixes may be cherry-picked into patch releases when necessary.


## Development Environment Setup

1. **Clone the Repository** \
Download the source code by cloning the GitHub repository:
```bash
$ git clone https://github.com/foss-for-synopsys-dwc-arc-processors/compiler-abi-extractor
```

2. **Install Python** \
Ensure Python is installed on the system:
```bash
$ sudo apt-get install python3
```

3. **Set Up the Toolchain and Simulator** \
Make sure the required toolchain and simulator are available in the `PATH`. By default, the compiler is `riscv32-unknown-elf-gcc`, and the simulator is `qemu-riscv32`.

4. **Run the Project** \
Start the application with the following command:
```bash
$ python3 abi-extract-info
```


## Reference Reports

The `reports/` directory contains references of what the reports should contain.
If analyzers are added, or changed in any other way, please update the reference
reports in this directory.


## Sign Your Commits

Licensing is important to open source projects. It provides some assurances that
the software will continue to be available based under the terms that the
author(s) desired. We require that contributors sign off on commits submitted to
our project's repositories. The [Developer Certificate of Origin
(DCO)](https://probot.github.io/apps/dco/) is a way to certify that you wrote and
have the right to contribute the code you are submitting to the project.

You sign-off by adding the following to your commit messages. Your sign-off must
match the git user and email associated with the commit.

    This is my commit message

    Signed-off-by: Your Name <your.name@example.com>

Git has a `-s` command line option to do this automatically:

    git commit -s -m 'This is my commit message'

If you forgot to do this and have not yet pushed your changes to the remote
repository, you can amend your commit with the sign-off by running

    git commit --amend -s
