# The Savings Game

## Overview
The Savings Game is an intertemporal savings and consumption behavioral economics task designed to measure how inflation impacts individuals' economic decision making. It is designed to integrate into online and laboratory-based behavioral experiments.

The Savings Game operates on the [oTree framework](https://www.otree.org/), using Python, JavaScript, and HTML/CSS.

## Installation
To install and run the Savings Game locally, you will need to ensure to have the requesite dependencies (libraries, packages, etc.), including Python, oTree, and others.
### Using a virtual environment
The simplest way to ensure you correctly install everything is by using a `conda` virtual environment. If you do not have Anaconda installed on your computer, install it first [here](https://www.anaconda.com/download).

Once Anaconda is installed and you have cloned this project repository locally, open a terminal, either in your preferred code-editor (IDE) or directly from your desktop. Navigate to the repository's directory (i.e. folder) in the terminal and execute the following command: `conda env create --name the_savings_game --file environment.yml`. This will install all the required dependencies with the appropriate version simultaneously. It will also create a 'virtual environment,' which you must activate prior to running the Savings Game.

After the virtual environment creation concludes, activate it by executing the command in the terminal: `conda activate the_savings_game`. If succesfully activated, you should see `(the_savings_game)` appear to the left of the folder path in your terminal on the newest line. 

*Congratulations! You are now ready to run the Savings Game.*

## Running the Savings Game
To run the Savings Game locally, open your terminal, either in your preferred code-editor (IDE) or directly from your desktop, and navigate to the repository's directory (i.e. folder) in the terminal. If you created a virtual environment, first activate it using `conda activate the_savings_game`.

Next, execute: `otree devserver`. If successful, the following message should appear:
```
Open your browser to http://localhost:8000/
To quit the server, press Control+C.
```

Open a web browser and navigate to the address `http://localhost:8000/`. The screen below should appear in the window.
![image](https://github.com/le-nate/the_savings_game/assets/99023298/e927dcb3-d6be-4091-bd96-fe6dd7213cb2)


## Modules
### `task`

### `instructions`

### `session_results`

### `filler`



