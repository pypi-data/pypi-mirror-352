"""
This file contains the internal / library functions for parsing the output
of 'git log -p --format=raw --show-signature --stat'
There is intentionally no main function / CLI here, only testable and importable
functions to perform the parsing. CLI, and additional tracking, summaries etc.
are implemented in git_log_raw_parser.py

This is done in 4 steps:
1. Iterate over the input stream generating lines
2. Iterate over lines, find where the next commit starts, and generate "raw commits" (list of lines within one commit)
3. Iterate over raw commits, find where each section starts, and generate "split commits"
4. Iterate over the split commits, generating pretty commits.

All of this is implemented using generators / iterators, so you can process and output results
while later commits are still being printed / processed.

Performance-wise, the 4 step parsing outlined above is not ideal, but it helps a lot
in making the code simpler to write and read and less error prone.
In pracitce, performance is good enough, even for hundreds, or thousands commits.

If you want to operate on the more raw data without much translations / prettifying,
you can skip step 4, or steps 3 and 4.

Note: The output of the git log command we use varies based on gpg (which keys are imported).
      Don't expect the same output on different machines with different gpg states.

Note: The parsing is lossy, we reconfigure the input stream to replace unicode
      errors (with question marks), so don't expect the diffs or commit messages to be
      100% correct for these cases.
"""

import sys
from io import TextIOWrapper


def _reconfigure(input_stream):
    # input_stream / sys.stdin is defined as TextIO in typeshed even though it's actually TextIOWrapper by default
    # This decision was made because it's common to reassign stdin / stdout / stderr:
    # https://github.com/python/typeshed/issues/10093
    # For this parser we need to use reconfigure from TextIOWrapper, so we don't
    # encounter exceptions for commit messages / diffs with weird characters.
    # So we need to assume that sys.stdin is actually TextIOWrapper,
    # the assertion makes this assumption explicit and makes strict typecheckers like Pyright happy.
    assert isinstance(input_stream, TextIOWrapper)
    input_stream.reconfigure(errors="replace")


# Utilities:


def remove_prefix(line, prefix):
    assert line.startswith(prefix)
    offset = len(prefix)
    assert offset > 0
    return line[offset:]


def remove_suffix(line, suffix):
    assert line.endswith(suffix)
    offset = len(suffix)
    assert offset > 0
    return line[0:-offset]


def parse_author(line):
    author = {}
    split = line.split(" ")
    timezone = split[-1]
    timestamp = split[-2]
    suffix = " " + " ".join(split[-2:])
    full = remove_suffix(line, suffix)
    author["id"] = full
    assert full[-1] == ">"
    full = full[0:-1]
    split = full.split("<")
    assert len(split) == 2
    author["name"] = split[0].strip()
    author["email"] = split[1].strip()
    author["timestamp"] = timestamp
    author["timezone"] = timezone
    return author


def valid_signature(commit):
    for line in commit["gpg"]:
        if line.startswith("Good signature from "):
            return True
    return False


# The main parsing function to use in most cases:


def parse(input_stream=None, replace_errors=True):
    if input_stream is None:
        input_stream = sys.stdin
    if replace_errors:
        _reconfigure(input_stream)
    lines = input_stream_to_lines(input_stream)
    raw_commits = lines_to_raw_commits(lines)
    split_commits = raw_commits_to_split_commits(raw_commits)
    pretty_commits = split_commits_to_pretty_commits(split_commits)
    for pretty_commit in pretty_commits:
        # TODO: Do we want to do something more here?
        yield pretty_commit


# Another version of parse() which gives you all 3 representations of a commit
# Mostly useful for debugging
def parse_to_all_representations(input_stream=None, replace_errors=True):
    if input_stream is None:
        input_stream = sys.stdin
    if replace_errors:
        _reconfigure(input_stream)
    lines = input_stream_to_lines(input_stream)
    raw_commits = lines_to_raw_commits(lines)
    for raw_commit in raw_commits:
        # These function normally operate on iterators which yield many elements
        # (the entire git log), but we can call them on a n=1 tuple as well:
        split_commit = next(raw_commits_to_split_commits((raw_commit,)))
        pretty_commit = next(split_commits_to_pretty_commits((split_commit,)))
        yield (raw_commit, split_commit, pretty_commit)


# The individual steps / iterators:


def input_stream_to_lines(input_stream):
    for line in input_stream:
        yield line


def lines_to_raw_commits(line_iterator):
    current_commit = []
    for line in line_iterator:
        assert line[-1] == "\n"
        line = line[0:-1]
        if line.startswith("commit "):
            # New commit, finalize previous
            if current_commit:
                yield current_commit
                current_commit = []
        current_commit.append(line)
    if current_commit:
        yield current_commit


def raw_commits_to_split_commits(raw_commits):
    for raw in raw_commits:
        commit = {}
        first_line = raw[0]
        assert len(first_line) == len("commit 680e160eef58249b1b896512d50f6342ad325f01")
        assert first_line.startswith("commit ")
        commit["commit"] = [first_line]
        lines = (l for l in raw[1:])
        line = next(lines)
        while line and line.startswith("gpg: "):
            if "gpg" not in commit:
                commit["gpg"] = []
            commit["gpg"].append(line)
            line = next(lines)

        if line and line.startswith("Primary key fingerprint: "):
            commit["Primary key fingerprint"] = [line]
            line = next(lines)

        if line and line.startswith("     Subkey fingerprint: "):
            commit["Subkey fingerprint"] = [line]
            line = next(lines)

        assert line and line.startswith("tree ")  # TODO: Always?
        if line and line.startswith("tree "):
            commit["tree"] = [line]
            line = next(lines)

        while line and line.startswith("parent "):
            if not "parent" in commit:
                commit["parent"] = []
            commit["parent"].append(line)
            line = next(lines)

        assert line and line.startswith("author ")  # TODO: Always?
        if line and line.startswith("author "):
            commit["author"] = [line]
            line = next(lines)

        assert line and line.startswith("committer ")  # TODO: Always?
        if line and line.startswith("committer "):
            commit["committer"] = [line]
            line = next(lines)

        if line and line.startswith("gpgsig "):
            commit["gpgsig"] = [line]
            line = next(lines)
            while not line.startswith(" -----END PGP SIGNATURE-----"):
                assert "BEGIN PGP SIGNATURE" not in line
                commit["gpgsig"].append(line)
                line = next(lines)
            assert line == " -----END PGP SIGNATURE-----"
            commit["gpgsig"].append(line)
            line = next(lines)
        try:
            while line == " ":
                line = next(lines)
            while line == "":
                line = next(lines)
            commit["message"] = []
            while line and line != "---":
                commit["message"].append(line)
                line = next(lines)
            if line and line == "---":
                commit["diff"] = []
                line = next(lines)
                for line in lines:
                    commit["diff"].append(line)
        except StopIteration:
            pass
        yield commit


def _remove_prefixes(commit):
    if "commit" in commit:
        commit["commit"][0] = remove_prefix(commit["commit"][0], "commit ")
    if "gpg" in commit:
        commit["gpg"] = [remove_prefix(x, "gpg: ") for x in commit["gpg"]]
    if "Primary key fingerprint" in commit:
        commit["Primary key fingerprint"][0] = remove_prefix(
            commit["Primary key fingerprint"][0], "Primary key fingerprint: "
        )
    if "Subkey fingerprint" in commit:
        commit["Subkey fingerprint"][0] = remove_prefix(
            commit["Subkey fingerprint"][0], "     Subkey fingerprint: "
        )
    if "tree" in commit:
        commit["tree"][0] = remove_prefix(commit["tree"][0], "tree ")
    if "parent" in commit:
        commit["parent"][0] = remove_prefix(commit["parent"][0], "parent ")
    if "author" in commit:
        commit["author"][0] = remove_prefix(commit["author"][0], "author ")
    if "committer" in commit:
        commit["committer"][0] = remove_prefix(commit["committer"][0], "committer ")
    if "gpgsig" in commit:
        commit["gpgsig"][0] = remove_prefix(commit["gpgsig"][0], "gpgsig ")


def _strip_lists(commit):
    assert "commit" in commit and len(commit["commit"]) == 1
    commit["commit"] = commit["commit"][0]
    assert "tree" in commit and len(commit["tree"]) == 1
    commit["tree"] = commit["tree"][0]


def split_commits_to_pretty_commits(split_commits):
    for commit in split_commits:
        final = {}
        for key, value in commit.items():
            final[key] = value
        _remove_prefixes(final)
        _strip_lists(final)
        if "gpgsig" in final:
            assert final["gpgsig"][0] == "-----BEGIN PGP SIGNATURE-----"
            signature = ["-----BEGIN PGP SIGNATURE-----"]
            for line in final["gpgsig"][1:]:
                assert line.startswith(" ")
                signature.append(line[1:])
            final["gpgsig"] = "\n".join(signature)

        assert "author" in final
        final["author"] = parse_author(final["author"][0])
        assert "committer" in final
        final["committer"] = parse_author(final["committer"][0])

        if "Primary key fingerprint" in final:
            del final["Primary key fingerprint"]

        if "gpg" in final:
            assert final["gpg"][0].startswith("Signature made ")
            final["valid_signature"] = True
            if not valid_signature(final):
                final["valid_signature"] = False
            final["fingerprint"] = remove_prefix(
                final["gpg"][1], "               using RSA key "
            )
            if "Primary key fingerprint" in final:
                del final["Primary key fingerprint"]

        assert "message" in final
        final["message"] = "\n".join(x[4:] for x in final["message"])
        yield final
