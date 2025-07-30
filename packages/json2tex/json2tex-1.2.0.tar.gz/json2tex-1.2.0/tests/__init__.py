# system modules
import unittest
import json
import subprocess

# internal modules
import json2tex


class Json2TexTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_atomic(self):
        self.assertSquenceEqual(
            json2tex.json2tex(d := 1), (f"\\newcommand{{asdf}}{{{d}}}",)
        )

    def test_list(self):
        self.assertSequenceEqual(
            tuple(json2tex.json2texcommands([1, 2, 3, 4])),
            (
                r"\newcommand{\First}{1}",
                r"\newcommand{\Second}{2}",
                r"\newcommand{\Third}{3}",
                r"\newcommand{\Fourth}{4}",
            ),
        )

    def test_dict(self):
        self.assertSequenceEqual(
            tuple(
                json2tex.json2texcommands(
                    {"bla": 1, "bli": {"blar": 2}, "blubb": 3}
                )
            ),
            (
                r"\newcommand{\Bla}{1}",
                r"\newcommand{\BliBlar}{2}",
                r"\newcommand{\Blubb}{3}",
            ),
        )

    def test_cli_stdio(self):
        p = subprocess.Popen(
            ["json2tex"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        d = [{"asdf": ["blar", 1, 2, "blubb"], "z": {}}, 1, ["b", 4]]
        stdout, stderr = p.communicate((inputjson := json.dumps(d)).encode())
        self.assertEqual(
            stdout.decode().strip(),
            "\n".join(outputtex := json2tex.json2texcommands(d)),
        )
