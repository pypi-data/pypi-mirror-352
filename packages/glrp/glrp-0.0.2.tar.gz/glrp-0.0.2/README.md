# glrp - git-log-raw-parser

A parser for parsing the command:

```bash
git log -p --format=raw --show-signature --stat
```

## Why?

The above command provides a lot of useful information about git commits, which we can analyze, including:

- Commit message
- Diffs
- Author name and email
- Committer name and email
- Timestamps
- GPG signature

On its own, git log does not output its information in a format which is easy for other programs to use.
So, this tool parses the output and turns it into JSON which is more easy to analyze and check.

## Installation

```bash
pipx install glrp
```

## Usage

Using it is simple, just run the `git log` command and pipe it to the standard input of `git_log_raw_parser`

```
git log -p --format=raw --show-signature --stat | python3 -m glrp --output-dir=./out/
```

Or perhaps a bit more realistic:

```
git clone https://github.com/cfengine/core
(cd core && git log -p --format=raw --show-signature --stat HEAD~500..HEAD 2>/dev/null) | python3 git_log_raw_parser.py
```

(Clone CFEngine core, start subshell which enters the subdirectory and runs git log for the past 500 commits).

## Important notes

**Warning:** The output of `--show-signature` varies depending on which keys you have imported / trusted in your installation of GPG.
Make sure you import the correct GPG keys beforehand, and don't expect output to be identical across different machines with different GPG states.

**Warning:** Consider this a best-effort, "lossy" parsing.
Commits may contain non utf-8 characters, to avoid "crashing", we skip these, replacing them with question marks.
Thus, the parsing is lossy, don't expect all the information to be there.
This tool can be used for searching / analyzing commits, but don't use it as some kind of backup tool where you expect to have the ability to "reconstruct" the commits and repo entirely.

## Details

For details on how the parsing works, try running with `--debug` and look at the resulting `./debug/` folder.
Also, see the comments in the source code; [./git_log_raw_parser.py](./git_log_raw_parser.py)
