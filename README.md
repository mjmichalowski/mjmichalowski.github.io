## Welcome to My Portfolio!

Below, you can find some of my work in Python and Matlab, as well as articles and reports I have written.

### Matlab Projects

1. [_Recurring Digits Finder_](matlab/project_1/Recurring_Digits_Report.pdf) - this project is based on number theory, specfically the decimal expansions of fractions. It aimed to quickly and efficiently find their repeating digits and the period length.

2. [_Fox and Rabbit Problem_](matlab/project_2/Fox_and_Rabbit_Report.pdf) - this project uses Matlab to solve a system of coupled PDEs. The scenario describes a rabbit running towards its burrow and a fox which is trying to catch the rabbit before it reaches safety, while avoiding obstacles on the way. The motion of the fox is deeply connected with the position of the rabbit and the barrier at any given point. The application of Matlab here can be widely used for many real-world dynamic scenarios.

3. [_Big Data Analysis_](matlab/project_3/Project_3_Report.pdf) - this project employs some of the techniques useful in analysing big data sets. It uses a large, imaginary set containing information (date, price, variety etc.) about natural products in order to present some key facts which could be used to make business decisions in this scenario. Naturally, these techniques are highly applicable in both scientific and business analysis.

### Python Projects

1. [_Finding the Width and Mass of a Z-Boson_](https://github.com/mjmichalowski/mjmichalowski.github.io/tree/main/python/z-boson) - this script analyses data sets of decays across differing energies. It assumes the process can be described as a first order Feynman diagram of an electron-positron pair annihilating into a Z-Boson, which then decays into a new particle-antiparticle pair. Notably, it uses _tkinter_ package to display a GUI from which the user can explore different options and perform the analysis. Object-oriented programming is employed to simplify the construction of the main loop of the GUI. The program is quite versatile in that it allows the user to:
  - change the decay products
  - provide external data sets using finder
  - display multiple plots
  - save the data and plots to a desired location.

2. [_Bouncy Ball_](https://github.com/mjmichalowski/mjmichalowski.github.io/blob/main/python/bouncy-ball/bouncy_ball.py) - a simple script calculating the number of bounces of a ball with a certain 'bounciness' coefficient above a preselected minimum height. It allows for customisation of all values involved in the problem, inputting unlimited amount of scenarios at once and plotting of the height-time graph for the ball. The data for multiple scenarios is aggregated and handled using pandas module - very commonly employed in data analysis. At the end, the user can also choose to export the results to a csv file.

3. [_Leitner Flashcard System_](https://github.com/mjmichalowski/mjmichalowski.github.io/blob/main/python/leitner-flashcards/leitner_flashcards.py) - a rather short program exploring the integration of SQL into python via SQLalchemy library. It allows the user to create their own flashcards and then study them using the [Leitner system](https://en.wikipedia.org/wiki/Leitner_system). The flashcards are stored in a separate database file, with all crucial information stored alongside. In practice, this means the program can be closed at any point and then the user can resume learning from that same point.

4. [_Markov Chains Text Generator_](https://github.com/mjmichalowski/mjmichalowski.github.io/tree/main/python/markov_chains) - this was a hobby script exploring the concept of [Markov chains](https://en.wikipedia.org/wiki/Markov_chain) in language. It accepts a large txt file as input and then uses the Natural Language Toolkit module to tokenize it into separate words (punctuation marks are included as parts of those words). It then constructs chains of 2 consecutive words followed by various 3rd words and the corresponding frequency of these combinations. Finally, 10 sentences are generated based on the relations 'learned' from these chains. In practice, only 20% of generated can be said to make sense when used with a txt file 1GB in size. However, it is a nice proof-of-concept program. To make it better, one could possibly reinforce it with a more holistic ML model which tries to find relationships on the scale of sentences rather than individual words.

### Equipment Database Guide for Joint Institute for Nuclear Research in Dubna

The following [_report_](various/report_jinr.pdf) was written at the end of a short project with the Joint Institute for Nuclear Research (JINR) in Dubna. The overarching aim of the project is to build an efficient Oracle-based equipment database, similar to one employed in the ALICE experiment, which would help facilitate research both in JINR and its international partners. The main portion of our work was to write a thorough guide to the workings of the database which could be used by the researchers and technicians. The report itself summarises this process and showcases the part of the guide written in the appendix.

### Laboratory Work
1. [_Measuring Galactic Rotation Curve_](various/Galactic_Hydrogen.pdf)

2. [_Measuring Drag Force Acting on Free-Falling Objects_](various/Drag_Forces_Michalowski.pdf)

### [Essay on Use of Perovskite in Solar Panels](various/Essay_Solar_Panels.pdf)

