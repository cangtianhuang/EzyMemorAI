from flask import Flask

from services.ui.chat_interface import ChatInterface


def create_app():
    app = Flask(__name__, template_folder='../ui/templates')
    chat = ChatInterface()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return chat.render()

    @app.route('/reset', methods=['POST'])
    def reset():
        return chat.reset()

    return app
