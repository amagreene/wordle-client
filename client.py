#!/usr/bin/env -S python3 -u

# usage: ./client <-p port> <-s> <hostname> <Northeastern-username>

import argparse
import socket
import json
import re
import ssl
import os
import sys

DEFAULT_PORT = 27993
DEFAULT_TLS_PORT = 27994

def init():
    parser = argparse.ArgumentParser(description="A client program that plays Wordle with the CS3700 server.")
    parser.add_argument("-p", "--port", help="specifies the TCP port that the server is listening on (default=27993)", type=int, required=False)
    parser.add_argument("-s", help="if given, the client will use an TLS encrypted socket connection", action="store_true", required=False)
    parser.add_argument("hostname", help="specifies the name of the server (DNS name or IP address in dotted notation)")
    parser.add_argument("Northeastern-username")
    return vars(parser.parse_args())


# Creates a list of potential Wordle answers from the contents of the words.txt file
def read_word_list():
    # opening the file in read mode
    # assumes that the words.txt file is in the same directory as the program
    words_file = open("words.txt", "r")
    # reading the file
    file_content = words_file.read()
    # turns file into list of strings
    words_list = file_content.split('\n')
    # cleanup: closes the file
    words_file.close()
    return words_list


# Determines the port number according to the given command line arguments.
def port_setup(s, p):
    # If -s is supplied and -p is not specified, we assume the port is 27994.
    if s and p is None:
        return DEFAULT_TLS_PORT 
    # Port is specified --> use the specified port
    elif p:
        return p
    else:
        return DEFAULT_PORT


# Creates a regular expressions pattern that uses the accuracy marks of the given guess to determine which
# letters appear (or don't appear) in the solution. This regex is used to filter the list of potential guesses.
def build_regex(guess, marks):

    # YELLOWS
    yellows = ["", "", "", "", ""]
    for i in range(len(guess)):
        letter = guess[i]
        if marks[i] == 1:  # tabulating all yellow marks
            yellows[i] = letter

    # GRAYS
    grays = ["", "", "", "", ""]
    for i in range(len(guess)):
        letter = guess[i]
        mark = marks[i]
        if mark == 0 and letter not in yellows:
            # we know the solution does not contain this letter anywhere
            grays = [w + letter for w in grays]
        elif mark == 0:
            # this letter exists elsewhere in the solution
            grays[i] = grays[i] + letter

    # create regex
    restrictions = ["", "", "", "", ""]
    for i in range(len(guess)):
        if marks[i] == 2:
            # GREENS
            restrictions[i] = guess[i]
        else:
            # use info from yellows and grays array, '^' means 'not'
            restrictions[i] = "[^" + yellows[i] + grays[i] + "]"

    # create lookahead section for regex (says that this letter exists in the solution)
    # ex: (?=.*t) means that the solution contains at least 1 't'
    # ex: ^(?=.*x.*x) means that the solution contains at least 2 'x's
    unique_yellows = list(yellows)
    lookaheads = ""
    for c in unique_yellows:
        if len(c) > 0:
            new_lookahead = "(?=" + ((".*" + c) * yellows.count(c)) + ")"
            lookaheads += new_lookahead
    # ^ means start, $ means end
    regex = "^" + lookaheads + "".join(restrictions) + "$"
    return regex


# Uses a regex to filter the list of potential guesses according to the previous guess's marks.
# Returns the first item in the filtered list and the list itself.
def find_first_guess(guess, marks, words):
    assert len(words) > 0  # checking for valid dict

    # use our regular expression to filter the invalid words out of the list of possible guesses
    pattern = build_regex(guess, marks)
    filtered_list = [word for word in words if re.match(pattern, word)]

    # our dictionary does not contain the correct answer...
    if len(filtered_list) == 0:
        return None, []
    # find_first will return the first word in the filtered list of valid words
    return filtered_list[0], filtered_list


# Creates a client socket that connects to the CS3700 Wordle server.
# Program will guess a words and send it to the server, then use the server's feedback to narrow down
# its search and send another guess to the server.
# After guessing correctly, run_client will print the flag it receives from the server.
def run_client(args):
    words_list = read_word_list()
    port = port_setup(args["s"], args["port"])

    # initialize the client's socket
    client_socket = socket.socket()
    # use TLS encrypted socket?
    if args["s"]:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client_socket = context.wrap_socket(client_socket)
    # connect the client socket to Wordle server
    client_socket.connect((args["hostname"], port))

    # hello & start message
    json_msg = '{"type": "hello", "northeastern_username": "' + args["Northeastern-username"] + '"}\n'
    client_socket.send(json_msg.encode())
    server_message = json.loads(client_socket.recv(1024).decode())
    if server_message["type"] != "start":
        raise RuntimeError("Unable to start Wordle with server :/")
    server_id = server_message["id"]

    # playing Wordle!

    # initial guess
    guess = "slate"

    while server_message["type"] != "bye":
        # send guess to server
        json_msg = '{"type": "guess", "id": "' + server_id + '", "word": "' + guess + '"}\n'
        client_socket.send(json_msg.encode())

        # receive server's response
        new_data = json.loads(client_socket.recv(1024).decode())
        while new_data != None:
            server_message += new_data
            new_data = json.loads(client_socket.recv(1024).decode())

        if server_message["type"] == "retry":
            past_guesses = server_message["guesses"]
            (guess, words_list) = find_first_guess(guess, past_guesses[len(past_guesses) - 1]["marks"], words_list)
            if guess is None:
                # the answer does not exist in our dictionary
                raise RuntimeError("Our dictionary does not contain the solution :/")

    print(server_message["flag"])
    # cleanup: closes the client's connection to the server
    client_socket.close()


if __name__ == '__main__':
    cmd_line_args = init()
    run_client(cmd_line_args)
