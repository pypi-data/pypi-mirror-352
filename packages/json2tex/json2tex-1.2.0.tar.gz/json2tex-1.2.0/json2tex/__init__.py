# system modules
import functools
import re
import json
import sys
import argparse
import operator

# internal modules

# external modules
import inflect


def latex_escape(string):
    """
    Prepend characters that have a special meaning in LaTeX with a backslash.
    """
    return functools.reduce(
        lambda s, m: re.sub(m[0], m[1], s),
        (
            (r"[\\]", r"\\textbackslash "),
            (r"[~]", r"\\textasciitilde "),
            (r"[\^]", r"\\textasciicircum "),
            (r"([&%$#_{}])", r"\\\1"),
        ),
        str(string),
    )


def numbers2words(s):
    p = inflect.engine()
    if isinstance(s, int):
        return p.ordinal(
            re.sub(r"\W+", r" ", p.number_to_words(s, andword="", comma=""))
        )
    numbers = re.findall(r"\d+", str(s))
    outs = s
    for number in numbers:
        words = re.sub(
            r"\W+", r" ", p.number_to_words(number, andword="", comma="")
        )
        outs = outs.replace(number, " {} ".format(words), 1)
    return outs


def elements2texmaxcroname(elements):
    p = inflect.engine()
    return re.sub(
        r"\s+",
        r"",
        " ".join(
            map(
                operator.methodcaller("title"),
                map(
                    lambda w: re.sub(r"\W+", r" ", w),
                    map(numbers2words, elements),
                ),
            ),
        ),
    )


def dead_ends(d, path=tuple()):
    """
    Generator recursing into a dictionary and yielding tuples of paths and the
    value at dead ends.
    """
    if type(d) in (str, int, bool, float, type(None)):
        # print(f"Reached a dead end: {d}")
        yield path, d
        return
    elif hasattr(d, "items"):
        # print(f"recursing into dict {d}")
        for k, v in d.items():
            for x in dead_ends(v, path + (k,)):
                yield x
    else:
        try:
            it = iter(d)
            # print(f"recursing into list {d}")
            for i, e in enumerate(d):
                for x in dead_ends(e, path + (i + 1,)):
                    yield x
        except TypeError:
            # print(f"Don't know what to do with {d}. Assuming it's a dead
            # end.")
            yield sequence, d


def json2texcommands(d, escape=True):
    """
    Convert a JSON dict to LaTeX \\newcommand definitions

    Args:
        d (JSON-like object): the JSON to convert

    Yields:
        str : LaTeX \\newcommand definitions
    """
    # Traverse the merged inputs and output TeX definitions
    for name_parts, raw_value in dead_ends(d):
        name = elements2texmaxcroname(name_parts)
        value = latex_escape(raw_value) if escape else raw_value
        latex = f"\\newcommand{{\\{name}}}{{{value}}}"
        yield latex


def json2texfile(d, path, **kwargs):
    with path if hasattr(path, "write") else open(path, "w") as fh:
        for latex in json2texcommands(d, **kwargs):
            fh.write(f"{latex}\n")


def cli(cliargs=None):
    """
    Run :mod:`json2tex`'s command-line interface

    Args:
        cliargs (sequence of str, optional): the command-line arguments to use.
            Defaults to :any:`sys.argv`
    """
    parser = argparse.ArgumentParser(description="Convert JSON to TEX")
    parser.add_argument(
        "-i",
        "--input",
        help="input JSON file",
        nargs="+",
        type=argparse.FileType("r"),
        default=[sys.stdin],
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output TEX file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    parser.add_argument(
        "--no-escape",
        help="Don't do any escaping of special LaTeX characters",
        action="store_true",
    )
    args = parser.parse_args(cliargs)

    # Merge all inputs
    for f in args.input:
        d = json.load(f)
        try:
            JSON
        except NameError:
            JSON = d
            continue
        if isinstance(JSON, list):
            if isinstance(d, list):
                JSON.extend(d)
            else:
                JSON.append(d)
        elif isinstance(JSON, dict):
            if isinstance(d, dict):
                JSON.update(d)
            else:
                JSON = [JSON, d]

    json2texfile(JSON, path=args.output, escape=not args.no_escape)


if __name__ == "__main__":
    cli()
