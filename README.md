## Overview

This program creates a client socket that plays Wordle with the CS3700 server. The client sends 
the server a JSON message that includes a type and Wordle guess (or NEU username). Then the 
server responds with a JSON message that includes the message type and marks. Marks are a list
of numbers that represent feedback on the client's guess:

- 0 = gray, the solution does not contain this letter
- 1 = yellow, the solution contains this letter in a different position than the one guessed
- 2 = green, the solution contains this letter in the position guessed

After the client sends the correct guess to the server, the server responds with a secret flag.

The user can specify the port number and choose to use a TLS encrypted socket connection when
running this program from the command line. (See usage below.)

### Approach

This program solves Wordle by filtering a list of potential guesses according to regular
expressions search patterns. The client guesses the first word in the filtered list and
uses feedback from the server to continue filtering down the list of potential words.

For example, assume that the client guesses "treat" when the solution is "steam". The server
will respond with marks [1, 0, 2, 2, 0]. We can translate this information to regex like so:
- the solution contains a 't' —> (?=.*t)
- the 1st letter of the solution is not 't' —> [^t]
- the 2nd letter of the solution is not 'r' —> [^r]
- the solution does not contain 'r' —> [^r][^r][^r][^r][^r]
- the 3rd letter of the solution is 'e' —> e
- the 4th letter of the solution is 'a' —> a [^t]
- the 5th letter of the solution is not 't'

We can use these facts to create the regular expression "^(?=.*t)[^tr][^r]ea[^rt]$". Then we
can use Python's regex search engine to filter the list of possible guesses, leaving only the
words that contain a 't' somewhere, that do not start with 't' or 'r', and so on. This program
guesses the first word in the filtered list.

If the server responds that the guess in incorrect, this program will filter the list of potential
words again using the information it learned from its previous guess' marks (greens, yellows,
grays). This will repeat until the client sends the correct word to the server (and receives the
flag) or the dictionary runs out of potential guesses.


### Usage

client [-h] [-p PORT] [-s] hostname Northeastern-username

positional arguments:
  hostname              specifies the name of the server (DNS name or IP address in dotted notation)
  Northeastern-username

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  specifies the TCP port that the server is listening on (default=27993)
  -s                    if given, the client will use an TLS encrypted socket connection


## Testing

The "test.py" file contains automated testing of the Wordle solving algorithm.
This includes:
- Reading elements in the local file of potential Wordle solutions
- Correctly setting up the client's port according to command line arguments
- Using accuracy marks from the server (green, yellow, gray letters) to build an appropriate
  regular expression
- Filtering a list of words so that all follow the regex pattern

I manually tested the run_client function to make sure that the program could connect to the
CS3700 server using a regular and TLS encrypted socket. These tests were successful because
the client received two flags from the server, which are stored in the "secret_flags" file.


## Challenges

I've never written regular expressions before this project — a CS/Linguistics friend taught 
me the basics and inspired me to use regex to solve this assignment. Using regex to handle
the Wordle edge cases was tricky. Through trial and error, I learned that gray marks can't 
say for certain that the solution does not have a certain letter (ie if the guess has duplicate
letters where 1 is green and 1 is gray). I tested cases like this in the "test.py" file to
ensure that the program generated appropriate regex patterns.

It was also a challenge learning how to create a client socket and connect to the server. I read
many Python tutorials on the ssl and socket libraries and referenced the documentation often
while creating and troubleshooting my run_client function. These are the references I used:
- https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client
- https://realpython.com/python-sockets/
- https://docs.python.org/3.3/library/ssl.html#module-ssl
- https://docs.oracle.com/javase/8/docs/api/javax/net/ssl/SSLContext.html
- https://docs.python.org/3/library/argparse.html
