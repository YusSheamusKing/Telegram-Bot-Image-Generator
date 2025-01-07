# Telegram Bot for Image Generation

This Telegram bot allows users to generate images based on provided prompts and styles using the Stability AI image generation API. The project is organized into three main files: `main.py` `helper.py` and `generate_html.py`.

## Table of Contents

- [Telegram Bot for Image Generation](#telegram-bot-for-image-generation)
  - [Table of Contents](#table-of-contents)
  - [1. Files and Structure](#1-files-and-structure)
    - [1.1 `main.py`](#11-mainpy)
    - [1.2 `helper.py`](#12-helperpy)
    - [1.3 `generate_html.py`](#13-generatehtmlpy)
  - [2. Getting Started](#2-getting-started)
    - [2.1 Prerequisites](#21-prerequisites)
    - [2.2 Setting up Environment Variables](#22-setting-up-environment-variables)
    - [2.3 Running the Bot](#23-running-the-bot)
  - [3. Usage](#3-usage)
  - [4. Directory Structure](#4-directory-structure)
  - [5. Notes](#5-notes)

---

## 1. Files and Structure

### 1.1 `main.py`

This file serves as the main entry point for the Telegram bot. It contains the following key components:

- **Telegram Bot Setup**: Import required libraries, load environment variables, and configure logging.
- **State Constants**: Constants for different states of the conversation.
- **Conversation Handling**: Set up a ConversationHandler to manage user interactions.
- **Image Generation data**: Functions like `image` and `handle_text` to handle user commands and inputs.
- **Telegram Bot Initialization**: Set up the Telegram bot, add handlers, and start the bot.

### 1.2 `helper.py`

This file contains utility functions related to image generation. It includes:

- **Image Generation Function**: The `generate_image` function takes user prompts and styles as input and interacts with the Stability AI API to generate images.

### 1.3 `generate_html.py`

This file is responsible for generating an HTML file (`index.html`) that displays a gallery of images along with their associated metadata. It includes:

- **Folder and File Management**: The script scans the specified `bot/image` folder to find `.png` images and their corresponding `.txt` metadata files.

- **Metadata Extraction**: Extracts details like:
  - **Prompt**: Description of the image.
  - **Style**: Style applied during image generation.
  - **Size**: Dimensions of the image.
  - **User Information**: Username and additional user details if available.
  - **Price**: Indicates whether the image is for sale or not.

- **HTML Generation**:
  - Dynamically creates a gallery layout using HTML and CSS.
  - Includes a **filtering feature** powered by JavaScript, allowing users to filter images based on:
    - Prompt.
    - Style.
    - User.
    - Minimum price.

- **Output File**: Generates a fully-styled `index.html` file in the project directory, which can be viewed in any browser.

This script is integral for transforming generated images into a user-friendly gallery format that includes interactive filtering for better usability.

## 2. Getting Started

Follow these steps to set up and run the Telegram bot:

### 2.1 Prerequisites

- Python 3.11 or higher installed on your system.
- Required libraries: `python-telegram-bot`, `requests`, `dotenv`  `flask`. Install them using:

  ```bash
  pip install python-telegram-bot requests python-dotenv flask
  ```

### 2.2 Setting up Environment Variables

1. Create a `.env` file in the project directory.
2. Add the following entries to the `.env` file:

    ```dotenv
    STABILITY_API_KEY=your_stability_api_key
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    USER_ID="*" # comma for separation, '*' to enable all user access.
    ADMIN_ID="*" # comma for separation, '*' to enable all user access.
    ```

    Replace `your_stability_api_key`, `your_telegram_bot_token` and user and/or admin id  with your Stability AI API key, Telegram bot token and telegram id, respectively.

### 2.3 Running the Bot

Run the `main.py` script to start the Telegram bot:

```bash
python main.py
```
Run the `generate_html.py` to start the Gallery:
```bash
python generate_html.py
```

The bot is now active and ready to respond to commands.

## 3. Usage

1. Start a conversation with the Telegram bot.
2. Use the `/image` command to initiate the image generation process.
3. Use the `/cancel` button to cancel image generation process.
4. Follow the prompts to provide input for image generation, including prompts size and style selections.
5. The bot will process the input, generate an image using the Stability AI API, and send the generated image back to the user.
6. Additionally user can set a prize for an image
7. After that user can enter the website (run generate_html.py) and enter the website.
8. Therefore , user can search using filter also by navigating to price they can contact the other user

## 4. Directory Structure

The project directory is organized as follows:

```plaintext
project-directory/
bot folder
│
  ├── main.py
  ├── helper.py
  ├──bot_users.db
  ├── .env
  └── image/
    ├── (generated images)
├──generate_html.py
```

- `main.py`: Main script for the Telegram bot.
- `helper.py`: Helper script containing utility functions.
- `.env`: Configuration file for storing environment variables.
- `out/`: Directory to store generated images.
- `generate_html.py` : Will create index.html to access a website  image gallery


## 5. Notes

- Ensure that the `./image` directory exists before running the bot. If not, it will be created during the image generation process.
- The bot requires a stable internet connection to interact with the Telegram API and Stability AI API.

---
