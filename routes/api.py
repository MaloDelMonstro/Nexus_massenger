from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import functools

from models import User
from plugins.base import PluginContext

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def require_api_key(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API ключ не предоставлен',
                'code': 'NO_API_KEY'
            }), 401

        user = User.query.filter_by(api_key=api_key).first()

        if not user:
            return jsonify({
                'success': False,
                'error': 'Неверный API ключ',
                'code': 'INVALID_API_KEY'
            }), 403

        if user.is_banned:
            return jsonify({
                'success': False,
                'error': 'Аккаунт заблокирован',
                'code': 'ACCOUNT_BANNED'
            }), 403

        request.api_user = user
        return f(*args, **kwargs)

    return decorated


@api_bp.route('/plugins/execute', methods=['POST'])
@require_api_key
def execute_plugin():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Тело запроса должно быть JSON',
                'code': 'INVALID_JSON'
            }), 400

        command = data.get('command', '').strip()
        args = data.get('args', [])

        if not command:
            return jsonify({
                'success': False,
                'error': 'Команда не указана',
                'code': 'NO_COMMAND'
            }), 400

        from flask import current_app
        manager = current_app.extensions.get('plugin_manager')

        if not manager:
            return jsonify({
                'success': False,
                'error': 'Система плагинов не инициализирована',
                'code': 'PLUGIN_MANAGER_NOT_READY'
            }), 500

        full_command = '/' + command
        if args:
            full_command += ' ' + ' '.join(str(a) for a in args)

        ctx = PluginContext(
            user_id=request.api_user.id,
            username=request.api_user.username,
            user_is_admin=request.api_user.is_admin,
            timestamp=datetime.now(timezone.utc)
        )

        response = manager.execute_command(full_command, ctx)

        if not response:
            return jsonify({
                'success': False,
                'error': 'Команда не найдена или не выполнена',
                'code': 'COMMAND_NOT_EXECUTED'
            }), 404

        return jsonify({
            'success': response.success,
            'message': response.message,
            'data': response.data,
            'ephemeral': response.ephemeral,
            'plugin': manager.registry.get_plugin(command).name if manager.registry.get_plugin(command) else None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200 if response.success else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {type(e).__name__}',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/plugins/list', methods=['GET'])
@require_api_key
def list_plugins():
    try:
        from flask import current_app
        manager = current_app.extensions.get('plugin_manager')

        if not manager:
            return jsonify({
                'success': False,
                'error': 'Система плагинов не инициализирована',
                'code': 'PLUGIN_MANAGER_NOT_READY'
            }), 500

        plugins = []
        for name, plugin in manager.plugins.items():
            if hasattr(plugin, 'required_role') and plugin.required_role == 'admin':
                if not request.api_user.is_admin:
                    continue

            plugins.append({
                'name': plugin.name,
                'description': plugin.description,
                'version': plugin.version,
                'author': plugin.author,
                'commands': plugin.commands,
                'cooldown': getattr(plugin, 'cooldown', 0),
                'required_role': getattr(plugin, 'required_role', None)
            })

        return jsonify({
            'success': True,
            'count': len(plugins),
            'plugins': plugins
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/plugins/help', methods=['GET'])
@require_api_key
def plugin_help():
    try:
        plugin_name = request.args.get('plugin', '').strip().lower()

        if not plugin_name:
            return jsonify({
                'success': False,
                'error': 'Укажите имя плагина: ?plugin=ban',
                'code': 'NO_PLUGIN_NAME'
            }), 400

        from flask import current_app
        manager = current_app.extensions.get('plugin_manager')

        if not manager:
            return jsonify({
                'success': False,
                'error': 'Система плагинов не инициализирована',
                'code': 'PLUGIN_MANAGER_NOT_READY'
            }), 500

        plugin = manager.plugins.get(plugin_name)

        if not plugin:
            return jsonify({
                'success': False,
                'error': f'Плагин "{plugin_name}" не найден',
                'code': 'PLUGIN_NOT_FOUND'
            }), 404

        if hasattr(plugin, 'required_role') and plugin.required_role == 'admin':
            if not request.api_user.is_admin:
                return jsonify({
                    'success': False,
                    'error': 'Доступ запрещён',
                    'code': 'ACCESS_DENIED'
                }), 403

        help_text = plugin.help() if hasattr(plugin, 'help') and callable(plugin.help) else plugin.description

        return jsonify({
            'success': True,
            'plugin': plugin.name,
            'help': help_text,
            'commands': plugin.commands,
            'version': plugin.version
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/me', methods=['GET'])
@require_api_key
def get_api_user():
    user = request.api_user

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email if user.privacy_show_email else None,
            'is_admin': user.is_admin,
            'is_bot': user.is_bot,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'avatar_url': user.avatar_url
        }
    }), 200
