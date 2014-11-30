Being a huge fan of toggl.com and its nice summary diagrams, what I always missed was historical graphs.
This small python program is meant to create such a graph.

To try this out, enter three command line arguments: start date, end date, and your user token (which can be found at the bottom of https://www.toggl.com/app/profile )

Example:
python chronicl.py 2014-08-20 2014-10-15 0853c89724897fd1877

You will then be prompted to choose a workspace, choose grouping by projects/clients, and pick individual projects/clients to compare and analyze.

You will get 2 plots, one with the graph itself and the other with the legend for it.


Dependencies:
- requests
- matplotlib
- base64, math, sys, re, datetime



This has been tested on a single paid account with no collaborators. I am not sure how it will work in multi-user workspaces.