# IPC Section Training for Chatbot

This directory contains scripts to train the chatbot to recognize all Indian Penal Code (IPC) sections and enhance its ability to respond to queries about IPC sections.

## Overview

The scripts in this directory implement a comprehensive training process for the chatbot to recognize and respond to queries about all IPC sections. The process involves:

1. Extracting all IPC sections from the database
2. Generating training examples for each section
3. Training the ML model with the comprehensive dataset
4. Enhancing the chatbot's pattern recognition for IPC section queries
5. Testing the chatbot's ability to recognize IPC sections

## Scripts

### 1. `train_all_ipc_sections.py`

This script extracts all IPC sections from the database, generates training examples for each section, and trains the ML model with the comprehensive dataset.

**Usage:**
```bash
python scripts/train_all_ipc_sections.py
```

**What it does:**
- Extracts all IPC sections from the database
- Generates multiple training examples for each section based on its code, name, and description
- Combines the new examples with existing training data
- Trains the ML model with the combined dataset
- Saves the training data to a new file with timestamp

### 2. `enhance_chatbot_ipc_recognition.py`

This script enhances the chatbot's ability to recognize and respond to queries about IPC sections by updating the pattern matching and response generation.

**Usage:**
```bash
python scripts/enhance_chatbot_ipc_recognition.py
```

**What it does:**
- Creates enhanced regex patterns for recognizing IPC section queries
- Updates the chatbot.py file to include the enhanced patterns
- Adds a method to check if a query is about any IPC section
- Enhances the query processing to better handle IPC section queries

### 3. `test_ipc_recognition.py`

This script tests the chatbot's ability to recognize and respond to queries about IPC sections after training.

**Usage:**
```bash
python scripts/test_ipc_recognition.py
```

**What it does:**
- Tests the chatbot's ability to recognize a random sample of IPC sections
- Tests more complex queries about IPC sections
- Tests the chatbot's ability to analyze complaints and identify applicable IPC sections
- Reports the success rate and logs detailed results

## Training Process

To train the chatbot to recognize all IPC sections, follow these steps:

1. Ensure that the database contains all the IPC sections you want to train on
2. Run the `train_all_ipc_sections.py` script to generate training examples and train the model
3. Run the `enhance_chatbot_ipc_recognition.py` script to enhance the chatbot's pattern recognition
4. Run the `test_ipc_recognition.py` script to verify that the training was successful

## Notes

- The training process may take some time, especially if there are many IPC sections in the database
- The scripts log detailed information about the training process, which can be useful for debugging
- The training data is saved to a new file with a timestamp, so you can keep track of different training runs
- The enhanced patterns are saved to a separate file, so they can be easily updated or modified

## Requirements

- Python 3.6 or higher
- Flask application with database containing IPC sections
- ML analyzer module with training functionality
- Chatbot module with pattern matching and response generation