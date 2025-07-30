LIGO Follow-up Advocate Tools
=============================

This package provides tools for LIGO/Virgo/KAGRA follow-up advocates to assist
in tasks such as drafting astronomical bulletins for gravitational-wave
detections.

To install
----------

The easiest way to install `ligo-followup-advocate`, is with `pip`:

    pip install --user ligo-followup-advocate

To upgrade
----------

Once you have installed the package, to check for and install updates, run the
following command:

    pip install --user --upgrade ligo-followup-advocate

Current templates
-----------------

If you wish to just see examples of the current templates or submit these to be
reviewed in P&P, you can find them [here](https://git.ligo.org/emfollow/ligo-followup-advocate/builds/artifacts/master/file/templates.pdf?job=publish).

Example
-------

`ligo-followup-advocate` provides a single command to draft a GCN Circular
skeleton. Pass it the authors and the GraceDB ID as follows:

    ligo-followup-advocate compose \
        'A. Einstein (IAS)' 'S. Hawking (Cambridge)' \
        'I. Newton (Cambridge)' 'Data (Starfleet)' \
        'S190407w'

Optionally, you can have the program open the draft in your default mail client
by passing it the `--mailto` option.

For a list of other supported commands, run:

    ligo-followup-advocate --help

For further options for composing circulars, run:

    ligo-followup-advocate compose --help

You can also invoke most functions directly from a Python interpreter, like
this:

    >>> from ligo import followup_advocate
    >>> text = followup_advocate.compose('S190407w')

To develop
----------

To participate in development, clone the git repository:

    git clone git@git.ligo.org:emfollow/ligo-followup-advocate.git

To release
----------

The project is set up so that releases are automatically uploaded to PyPI
whenever a tag is created. Use the following steps to issue a release. In the
example below, we are assuming that the current version is 0.0.5, and that we
are releasing version 0.0.6.

1.  Check the latest [pipeline status](https://git.ligo.org/emfollow/ligo-followup-advocate/pipelines)
    to make sure that the master branch builds without any errors.

2.  Make sure that all significant changes since the last release are
    documented in `CHANGES.md`.

3.  Update the heading for the current release in `CHANGES.md` from
    `0.0.6 (unreleased)` to `0.0.6 (YYYY-MM-DD)` where `YYYY-MM-DD` is today's
    date. Also update the version in `pyproject.toml` similarly.

4.  [Update the PDF templates](https://git.ligo.org/emfollow/ligo-followup-advocate/-/tree/master/ligo/followup_advocate/test/templates/templates.tex) with this new version.

5.  Commit those changes:

        git commit -a -m "Update changelog for version 0.0.6"

6.  Tag the release:

        git tag v0.0.6 -m "Version 0.0.6"

7.  Add a new section to `CHANGES.md` like this:

        ## 0.0.7 (unreleased)

        - No changes yet.

8.  Commit the changes:

        git commit -a -m "Back to development"

9. Push everything to GitLab:

        git push upstream && git push upstream --tags

    Within a few minutes, the new package will be built and uploaded to PyPI.

10. Upload PDF of templates created from the `publish` CI job to DCC. Initiate
   P&P review and address comments in a new release. Note that it may take
   multiple releases to get P&P approval.

11. [Create an SCCB ticket](https://git.ligo.org/computing/sccb/-/issues/new).
   Note that there is an option to do this via the a button in the CI/CD
   pipeline, but this template could be outdated. The recommendation is to
   create the ticket by hand via the above link.
