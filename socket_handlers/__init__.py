from .general import register_general_handlers
from .private import register_private_handlers


def register_socket_handlers(socketio):
    register_general_handlers(socketio)
    register_private_handlers(socketio)
