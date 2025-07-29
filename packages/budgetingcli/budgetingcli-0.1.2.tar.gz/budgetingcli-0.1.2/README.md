# Budgeting CLI

A simple command-line interface (CLI) tool for managing personal budgets. This tool allows users to create, view, and manage their budgets through a terminal interface.

## External Dependencies
- Install Ollama App: 
  - Follow the instructions at [Ollama Installation](https://ollama.com) to set up the Ollama.
  - download the model using:
    ```bash
    ollama run qwen3:8b
    ```
    - This will download the Qwen-3 8B model, which is used for processing and generating responses for the application


## Features
- Create and manage budgets
- Create profile
- View Progress
- View all spending
- Add spending
- Spending Forecasting

## Installation
- pip install budgetingcli (windows)
- pip3 install budgetingcli (macos)


## Usage
1. **Login**: Start the application by logging in with your credentials.
   ```bash
   budgetincli login
   ```