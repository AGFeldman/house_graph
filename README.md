This software scrapes data from http://donut.caltech.edu/directory about the membership of Caltech undergraduates in the eight different houses. This data is only accessible through the Caltech network.

Usage: python graph.py will prompt the user to enter a description of the group of undergraduates to consider, the file name to output, and whether to show undergraduates who are members of just one house.

This can also be run in one line from the terminal, without answering prompts, by running python graph.py "description" [-s] [outputname].

The -s option will cause the graph to show students who are members of just one house, and outputname is the name of the file to be output. If outputname is not specified, the file is named out.dot.

The output of graph is a DOT file. It should probably have a .dot or .gv extension, but the user is responsible for specifying the extension.

The graphviz program can be used to render DOT files. For example:
neato -Tpdf out.dot -o out.pdf

The graphs generated show the eight Caltech houses with their house colors. Individuals are represented as points. A black line from an individual to a house means that the individual is a full member of that house. A gray line means that the individual is a social member.

The group of students to consider is specified with set operations. This is most easily illustrated with an example. Let's say that you want to graph South Hovsers (students in Blacker, Dabney, Ricketts, and Fleming) who are math-CS double-majors. Using the prompt, find the codes corresponding to Blacker, Dabney, Ricketts, and Fleming. Currently, these are 47, 43, 48, and 44. Then, (47 | 43 | 48 | 44) represents the union of {students in Blacker}, {students in Dabney}, {students in Ricketts}, and {students in Fleming}. You should also find the codes for the Math and Computer Science majors. Currently, these codes are 87 and 95, so (87 & 95) represents the intersection of {students who are math majors} and {studnets who are Computer Science majors}. So, (47 | 43 | 48 | 44) & (87 & 95) represents math-CS double majors in the South Hovses. If you'd like to consider only current students, you could use (47 | 43 | 48 | 44) & (87 & 95) & (16 | 30 | 31 | 32), since 16, 30, 31, and 32 are the codes for students in the class of 2017, 2016, 2015, and 2014.

The codes are printed to the command line when python graph.py is run. They are not printed when graph is run with additional command-line arguments. However, every time the program is run, the list of codes is written to the text file user_choices.txt for easy reference.

Codes may change as the website changes.

The get_member_info module does all of the scraping data from the web. The graph module uses get_member_info and writes the DOT files, based on template.dot. 

This software is written in Python 2.7.5.
