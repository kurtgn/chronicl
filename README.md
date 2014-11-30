Being a huge fan of toggl.com and its nice summary diagrams, what I always missed was historical graphs.
This small python program is meant to create such a graph.

To try this out, enter three command line arguments: start date, end date, and your user token (which can be found at the bottom of https://www.toggl.com/app/profile )

Example:
python chronicl.py 2014-08-20 2014-10 0853c89724897fd1877

You will then be prompted to choose a workspace, choose grouping by projects/clients, and pick individual projects/clients to compare and analyze.


Dependencies:
- requests
- matplotlib
- base64, math, sys, re, datetime