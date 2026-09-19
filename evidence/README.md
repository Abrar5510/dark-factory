# Evidence

One file per stage, written by the checking seat when the stage is accepted.
Each records the commands that were run and the output that came back: the
project's checks, and the build-and-run gate in an isolated container with no
network.

The point is that a reader can re-run the same commands and get the same
result, rather than take a claim on trust.
