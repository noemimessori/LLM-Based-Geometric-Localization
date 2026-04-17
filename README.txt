# Assignement 4 : LLM-Based Geometric Localization in a Simulated Environment

## Group

- **Dominic Schneider** up202401395
- **Noemi Messori** up202401607
- **Hugo Hovhannessian** up202402934

## Title
Assignement 4 of Robotic Intelligent

## Purpose
The purpose of this project is to try to make a robot know where he is based on
LLM answers. This project was made in the context of our school year 2024/2025 at the
FEUP - Faculdade de Engenharia da Universidade do Porto in the class of Robótica Inteligente (M.EIC041)

<img src="images/feup_logo.png" alt="FEUP_logo" width="200"/>

## Process
First of all we manage to create a Python environnement

## Directory
```
├── GoogleAPI 
│    └── Google_api.txt         <-- the place were to put your api key for google Gemini to work
├── images 
│    ├── 01.png                 <-- the picture of the example 1
│    ├── 02.png                 <-- the picture of the example 2
│    ├── 03.png                 <-- the picture of the example 3 
│    ├── 04.png                 <-- the picture of the example 4 
│    ├── 05.png                 <-- the picture of the example 5 
│    ├── 06.png                 <-- the picture of the example 6 
│    └── feup_logo.png          <-- the logo of the FEUP 
├── localization_tests 
│    ├── math_prompt.txt        <-- the file with math prompt
│    ├── prompt_0.1.txt         <-- the first draft of the prompt
│    ├── prompt_0.2.txt         <-- the second draft of the prompt
│    ├── prompt_standard.txt    <-- the file with standard prompt
│    ├── reason_prompt.txt      <-- the file with reason prompt 
│    ├── test_data.csv          <-- the file with experimental conditions on csv format
│    └── test_data.txt          <-- the file with experimental conditions
├── GeminiAPI.py                    <-- The python file that permit to ask Gemini and input the current answer
├── LlamaAPI.py                     <-- The python file that permit to ask Llama and input the current answer
├── TrilaterationLocalizer.py       <-- A python file to see if we are more accurate by using just the Trilateration
├── VisualisationMathPrompt.py      <-- file that show how close every LLM answered with the math prompt
├── VisualisationReasoningPrompt.py   <-- file that show how close every LLM answered with the math reasoning
├── VisualisationStandardPrompt.py    <-- file that show how close every LLM answered with the math standart 
└── WorldTests.py                   <-- the file that build our world and permit us to test Gemini 
```

## How to launch our project : 
### WorldTests.py
To run this python file, you need to have your Gemini API Key put on a text file and put on the GoogleAPI directory
Then, just by clicking on run or by doing the command ``python WorldTests.py``

### VisualisationXXXXXXXPrompt.py 
To run this python file, you don't need any other specific tools or technical point to run everything. 
You can run it on your IDE or use the command ``python VisualisationXXXXXXXPrompt.py``

### LlamaAPI.py
To launch LlamaAPI.py you need to have [Olama](https://ollama.com) installed and to have some version of Llama installed too. 
If your version of Llama is different from ours (Llama 3.2) please modify the line 19 of the python file and you will
be able to launch it without trouble. 

### Link to github:
https://github.com/schnedom/RoboticaInteligente_Ass2.git

