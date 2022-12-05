# Telegram GPT assistant
GPT3 Telegram bot assistant

## Installation

```sh
pip install -r requirements.txt

playwright install
```

Create `.env` with:

```
BOT_TOKEN    = <TELEGRAM_TOKEN>
API_USER     = <OPENAI_USER>
API_PASSWORD = <OPENAI_PASSWORD>
```

## Run

Execute simultaneously:

```sh
python server.py
```

```sh
python bot.py
```

## Acknowledgements

Reused the https://chat.open.ai automation by [Daniel Gross](https://github.com/danielgross/whatsapp-gpt/blob/main/server.py).
