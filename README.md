# English Learning Telegram Bot

## Description

This Telegram bot aims to help users improve their English vocabulary. The bot saves words that the user wants to learn and quizzes them based on the Leitner System. The bot also saves user data, including profile pictures, to a JSON file.

## Features

- Add new words to your learning list
- Timed quizzes based on the Leitner System
- Grading of quiz answers
- Saving user data, including profile pictures

## Getting Started

### Prerequisites

- Python 3.x
- python-telegram-bot library

### Installation

1. Clone the repository
   \`\`\`
   git clone https://github.com/yourusername/english-learning-telegram-bot.git
   \`\`\`

2. Navigate to the project directory
   \`\`\`
   cd english-learning-telegram-bot
   \`\`\`

3. Install the required packages
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

### Usage

1. Create a new bot on Telegram's BotFather and get the API token.
2. Add the API token to a \`.env\` file like this:
   \`\`\`
   TELEGRAM_API_TOKEN=your_token_here
   \`\`\`

3. Run the bot
   \`\`\`
   python main.py
   \`\`\`

## Code Structure

- \`main.py\`: The main script to run the bot
- \`users.json\`: Stores user data in JSON format
- \`/pictures\`: Directory to store user profile pictures

## Contributing

Feel free to submit pull requests or open issues to improve the bot.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
