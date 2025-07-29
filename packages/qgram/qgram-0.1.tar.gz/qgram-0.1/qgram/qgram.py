import requests
import time
from typing import Dict, Optional, Union, List

class Bot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.command_handlers = {}
        self.message_handlers = []
        self.photo_handlers = []  # Handler for images
        self._current_context = None
        self.running = False
        self.last_bot_messages: Dict[int, int] = {}  # {chat_id: message_id}

    def on_command(self, command: str):
        """Decorator for registering command handlers"""
        def decorator(func):
            self.command_handlers[command] = func
            return func
        return decorator

    def on_message(self, func):
        """Decorator for text message handlers"""
        self.message_handlers.append(func)
        return func

    def on_photo(self, func):
        """Decorator for photo message handlers"""
        self.photo_handlers.append(func)
        return func

    def send(self, text: str, chat_id: Optional[int] = None) -> Dict:
        """
        Sends a message to the specified chat
        :param text: Message text
        :param chat_id: Chat ID (if None, uses current context)
        :return: Telegram API response
        """
        if chat_id is None and self._current_context:
            chat_id = self._current_context.message.get('chat', {}).get('id')

        if not chat_id:
            raise ValueError("Chat ID must be specified")

        url = f"https://api.telegram.org/bot{self.api_key}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, params=params)

        if response.ok:
            message_id = response.json().get('result', {}).get('message_id')
            if message_id:
                self.last_bot_messages[chat_id] = message_id

        return response.json()

    def send_photo(self, photo_url: str, caption: str = "",
                   chat_id: Optional[int] = None) -> Dict:
        """
        Sends a photo to the specified chat
        :param photo_url: URL of the photo
        :param caption: Photo caption
        :param chat_id: Chat ID
        :return: Telegram API response
        """
        if chat_id is None and self._current_context:
            chat_id = self._current_context.message.get('chat', {}).get('id')

        if not chat_id:
            raise ValueError("Chat ID must be specified")

        url = f"https://api.telegram.org/bot{self.api_key}/sendPhoto"
        params = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption
        }
        response = requests.post(url, params=params)
        return response.json()

    def delete(self,
               chat_id: Optional[int] = None,
               message_id: Optional[int] = None) -> Dict:
        """
        Deletes a message in chat
        :param chat_id: Chat ID (if None, uses current context)
        :param message_id: Message ID (if None, uses last sent message)
        :return: Telegram API response
        """
        if chat_id is None and self._current_context:
            chat_id = self._current_context.message.get('chat', {}).get('id')

        if message_id is None and chat_id in self.last_bot_messages:
            message_id = self.last_bot_messages.get(chat_id)

        if not chat_id or not message_id:
            raise ValueError("Chat ID and Message ID must be specified")

        url = f"https://api.telegram.org/bot{self.api_key}/deleteMessage"
        params = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        response = requests.post(url, params=params)
        return response.json()

    def get_file_url(self, file_id: str) -> str:
        """
        Returns file URL by its ID
        :param file_id: Telegram file ID
        :return: File download URL
        """
        # Get file info
        file_info_url = f"https://api.telegram.org/bot{self.api_key}/getFile?file_id={file_id}"
        file_info = requests.get(file_info_url).json()

        if file_info.get('ok'):
            file_path = file_info['result']['file_path']
            return f"https://api.telegram.org/file/bot{self.api_key}/{file_path}"
        return ""

    def process_message(self, message: Dict):
        """Processes incoming message"""
        context = Context(message, self)
        self._current_context = context

        # Command processing (works for both text and photo captions)
        command_text = message.get('text', '') or message.get('caption', '')
        if command_text and command_text.startswith('/'):
            command = command_text.split()[0][1:].split('@')[0]
            if command in self.command_handlers:
                try:
                    self.command_handlers[command](context)
                except Exception as e:
                    print(f"Error in command handler: {e}")
                return

        # Photo processing
        if 'photo' in message and self.photo_handlers:
            for handler in self.photo_handlers:
                try:
                    handler(context)
                except Exception as e:
                    print(f"Error in photo handler: {e}")
            return

        # Text message processing
        if 'text' in message and self.message_handlers:
            for handler in self.message_handlers:
                try:
                    handler(context)
                except Exception as e:
                    print(f"Error in message handler: {e}")

    def start_polling(self, interval: int = 1, timeout: int = 30):
        """Starts infinite polling loop"""
        self.running = True
        offset = 0

        print("Bot started polling...")
        while self.running:
            try:
                url = f"https://api.telegram.org/bot{self.api_key}/getUpdates"
                params = {
                    'offset': offset,
                    'timeout': timeout,
                    'allowed_updates': ['message', 'photo']
                }

                response = requests.get(url, params=params)
                data = response.json()

                if not data.get('ok', False):
                    print(f"API Error: {data.get('description', 'Unknown error')}")
                    time.sleep(interval)
                    continue

                for update in data.get('result', []):
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        self.process_message(update['message'])

            except requests.exceptions.RequestException as e:
                print(f"Connection error: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1)

    def stop(self):
        """Stops the bot"""
        self.running = False


class Context:
    def __init__(self, message: Dict, bot: 'Bot'):
        self._message = message
        self._bot = bot

    @property
    def message(self) -> Dict:
        """Returns the original message"""
        return self._message

    @property
    def bot(self) -> 'Bot':
        """Returns the bot instance"""
        return self._bot

    def get(self, key: Optional[str] = None, default=None) -> Union[Dict, any]:
        """
        Gets value from message
        :param key: Key (if None, returns entire message)
        :param default: Default value
        """
        if key is None:
            return self._message
        return self._message.get(key, default)

    @property
    def text(self) -> str:
        """Returns message text"""
        return self._message.get('text', '')

    @property
    def caption(self) -> str:
        """Returns photo caption"""
        return self._message.get('caption', '')

    @property
    def photo(self) -> List[Dict]:
        """Returns photo information from message"""
        return self._message.get('photo', [])

    @property
    def best_photo(self) -> Dict:
        """Returns highest resolution photo"""
        photos = self.photo
        if photos:
            # Photos are sorted by size, last one is the largest
            return photos[-1]
        return {}

    @property
    def photo_url(self) -> str:
        """Returns URL of the largest photo"""
        best_photo = self.best_photo
        if best_photo:
            file_id = best_photo.get('file_id')
            return self._bot.get_file_url(file_id)
        return ""

    def delete(self) -> Dict:
        """Deletes the bot's last message in this chat"""
        return self._bot.delete()
