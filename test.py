#!/usr/bin/env -S python3 -u
from client import read_word_list, port_setup, build_regex, find_first_guess


def check_expect(actual, expected):
    try:
        assert expected == actual
        print("Test passed.")
    except AssertionError:
        print("Test failed!")
        print("expected: " + expected)
        print("actual: " + actual)


def test_read_word_list():
    words_list = read_word_list()
    check_expect(len(words_list), 15918)
    check_expect(words_list[0], "aahed")
    check_expect(words_list[len(words_list) - 1], "zunis")


def test_port_setup():
    # no -s, no -p --> 27993
    check_expect(port_setup(None, None), 27993)
    # no -s, yes -p --> specified p
    check_expect(port_setup(None, 5), 5)
    # yes -s, no -p --> 27994
    check_expect(port_setup(True, None), 27994)
    # yes -s, yes -p --> specified p
    check_expect(port_setup(True, 5), 5)


def test_build_regex():
    # tests all unique letters
    check_expect(build_regex("quite", [2, 2, 1, 0, 0]), "^(?=.*i)qu[^ite][^te][^te]$")
    check_expect("^[^bui][^bui][^bui]ld$", build_regex("build", [0, 0, 0, 2, 2])) # no look ahead section

    # tests duplicate letters, 1 yellow & 1 gray
    check_expect(build_regex("treat", [1, 0, 2, 2, 0]), "^(?=.*t)[^tr][^r]ea[^rt]$")

    # tests duplicate letters, 1 yellow & 1 green
    check_expect(build_regex("loots", [0, 1, 2, 0, 0]), "^(?=.*o)[^lts][^olts]o[^lts][^lts]$")

    # tests duplicate letters, 1 gray & 1 green (e), 1 yellow & 1 gray (t)
    check_expect(build_regex("teeth", [0, 0, 2, 1, 1]), "^(?=.*t)(?=.*h)[^te][^e]e[^te][^he]$")
    # only 1 e (out of the 2 present) was green --> all other letters are not e
    # only 1 t (out of the 2 present) was yellow --> 1 t exists in the word and t is not in the 1st or 4th position

    # tests duplicate letters, 2 yellow
    # print(build_regex("toast", [1, 0, 2, 1, 1]))
    check_expect(build_regex("toast", [1, 0, 2, 1, 1]), "^(?=.*t.*t)(?=.*s)(?=.*t.*t)[^to][^o]a[^so][^to]$")


def test_re_filter():
    check_expect(find_first_guess("quiet", [2, 2, 2, 1, 1], ["fleet", "quite", "quack"]), ("quite", ["quite"]))
    check_expect(find_first_guess("blind", [0, 0, 0, 0, 0], ["shots", "quite", "quack"]), ("shots", ["shots", "quack"]))
    check_expect(find_first_guess("blind", [1, 0, 0, 0, 0], ["shots"]), (None, []))


if __name__ == '__main__':
    test_read_word_list()
    test_port_setup()
    test_build_regex()
    test_re_filter()
