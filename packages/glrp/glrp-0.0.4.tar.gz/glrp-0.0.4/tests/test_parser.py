import sys

from cfbs.pretty import pretty

sys.path.append(".")
import glrp.internal_parser as internal_parser


def test_basic():
    with open("tests/first_commits.txt", "r") as f:
        lines = f.readlines()
    content = "".join(lines)
    result = internal_parser.parse_to_all_representations(lines, replace_errors=False)
    result = list(result)
    assert len(result) == 2
    assert len(result[0]) == 3
    raw_content = ""
    for raw_commit, split_commit, pretty_commit in result:
        raw_content += "\n".join(raw_commit) + "\n"
    assert raw_content == content

    expected = []
    with open("tests/expected-01.json", "r") as f:
        expected.append(f.read())
    with open("tests/expected-02.json", "r") as f:
        expected.append(f.read())
    end_result = internal_parser.parse(lines, replace_errors=False)
    end_result = [pretty(x) + "\n" for x in end_result]

    assert len(end_result) == 2
    assert end_result[0] == expected[0]
    assert end_result[1] == expected[1]
