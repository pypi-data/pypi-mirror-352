"""
Flask Web应用主文件
"""

import os
import json
import base64
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import threading
from typing import Dict, List, Any

from ..core import config, MCPTools, ImageProcessor, ChatAPI, FeedbackHandler


def create_app() -> Flask:
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.web_secret_key
    app.config['MAX_CONTENT_LENGTH'] = config.max_file_size
    
    # 初始化SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 存储应用实例以便其他地方使用
    app.socketio = socketio
    
    # 注册路由
    register_routes(app)
    register_socketio_events(socketio)
    
    return app


def register_routes(app: Flask):
    """注册HTTP路由"""
    
    @app.route('/')
    def index():
        """主页 - 直接显示反馈收集页面"""
        work_summary = request.args.get('work_summary', '')
        feedback_data = MCPTools.collect_feedback_core(work_summary)
        return render_template('feedback.html', **feedback_data)

    @app.route('/feedback')
    def feedback_page():
        """反馈收集页面"""
        work_summary = request.args.get('work_summary', '')
        feedback_data = MCPTools.collect_feedback_core(work_summary)
        return render_template('feedback.html', **feedback_data)

    @app.route('/status')
    def status_page():
        """系统状态页面"""
        system_info = MCPTools.get_system_info()
        return render_template('status.html', system_info=system_info)
    
    @app.route('/chat')
    def chat_page():
        """AI聊天页面"""
        chat_data = MCPTools.open_chat_interface_core()
        return render_template('chat.html', **chat_data)
    
    @app.route('/api/feedback', methods=['POST'])
    def submit_feedback():
        """提交反馈API"""
        try:
            data = request.get_json()
            text_content = data.get('text', '')
            images_data = data.get('images', [])
            
            # 处理图片数据
            images = []
            for img_data in images_data:
                try:
                    # 从base64解码图片
                    img_info = ImageProcessor.from_base64(img_data)
                    images.append(img_info)
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'图片处理失败: {str(e)}'
                    }), 400
            
            # 处理反馈
            result = MCPTools.process_feedback_submission(text_content, images)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'提交反馈失败: {str(e)}'
            }), 500
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """文件上传API"""
        try:
            if 'files' not in request.files:
                return jsonify({'success': False, 'message': '没有文件'}), 400
            
            files = request.files.getlist('files')
            results = []
            
            for file in files:
                if file.filename == '':
                    continue
                
                try:
                    # 验证文件
                    filename = secure_filename(file.filename)
                    file_data = file.read()
                    
                    is_valid, message = config.validate_file_upload(filename, len(file_data))
                    if not is_valid:
                        results.append({
                            'filename': filename,
                            'success': False,
                            'message': message
                        })
                        continue
                    
                    # 处理图片
                    img_info = ImageProcessor.load_from_bytes(file_data, f'上传: {filename}')
                    base64_data = ImageProcessor.to_base64(img_info)
                    
                    results.append({
                        'filename': filename,
                        'success': True,
                        'base64': base64_data,
                        'size': img_info['size'],
                        'format': img_info['format']
                    })
                    
                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'message': str(e)
                    })
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'文件上传失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/info')
    def system_info():
        """获取系统信息API"""
        return jsonify(MCPTools.get_system_info())
    
    @app.route('/api/test/connection')
    def test_api_connection():
        """测试API连接"""
        try:
            chat_api = ChatAPI()
            is_connected, message = chat_api.test_connection()
            return jsonify({
                'success': is_connected,
                'message': message
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            }), 500


def register_socketio_events(socketio):
    """注册WebSocket事件"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接"""
        print(f'客户端已连接: {request.sid}')
        emit('connected', {'message': '连接成功'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接"""
        print(f'客户端已断开: {request.sid}')
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """处理发送消息"""
        try:
            print(f"🔍 收到消息: {data}")
            text = data.get('text', '')
            images_data = data.get('images', [])
            message_history = data.get('history', [])

            print(f"📝 文本内容: {text}")
            print(f"🖼️ 图片数量: {len(images_data)}")
            print(f"📚 历史消息数: {len(message_history)}")

            # 处理图片数据
            images = []
            for img_data in images_data:
                try:
                    img_info = ImageProcessor.from_base64(img_data)
                    images.append(img_info)
                except Exception as e:
                    print(f"❌ 图片处理失败: {e}")
                    emit('error', {'message': f'图片处理失败: {str(e)}'})
                    return

            # 处理消息
            print("🔄 处理聊天消息...")
            result = MCPTools.process_chat_message(text, images, message_history)
            print(f"📊 消息处理结果: {result['success']}")

            if not result['success']:
                print(f"❌ 消息处理失败: {result['message']}")
                emit('error', {'message': result['message']})
                return

            # 发送用户消息确认
            print("✅ 发送用户消息确认")
            emit('user_message', {
                'message': result['user_message'],
                'timestamp': FeedbackHandler.create_feedback_result()['timestamp']
            })

            # 开始AI回复
            print("🤖 开始AI回复")
            emit('ai_message_start')

            # 创建AI API客户端并发送流式请求
            chat_api = ChatAPI()
            print(f"🔑 API配置检查: {chat_api.validate_api_config()}")

            # 保存当前session ID，避免上下文问题
            current_sid = request.sid

            def on_message_chunk(content):
                print(f"📨 AI回复片段: {content[:50]}...")
                socketio.emit('ai_message_chunk', {'content': content}, room=current_sid)

            def on_error(error_msg):
                print(f"❌ AI回复错误: {error_msg}")
                socketio.emit('ai_message_error', {'error': error_msg}, room=current_sid)

            def on_complete():
                print("✅ AI回复完成")
                socketio.emit('ai_message_complete', room=current_sid)

            # 发送流式消息
            print("🚀 发送流式API请求...")
            chat_api.send_message_stream(
                result['messages'],
                on_message_chunk,
                on_error,
                on_complete
            )

        except Exception as e:
            print(f"❌ WebSocket处理异常: {e}")
            import traceback
            traceback.print_exc()
            emit('error', {'message': f'发送消息失败: {str(e)}'})
    
    @socketio.on('clear_chat')
    def handle_clear_chat():
        """清空聊天记录"""
        emit('chat_cleared', {'message': '聊天记录已清空'})


class WebInterface:
    """Web界面管理器"""
    
    def __init__(self):
        self.app = None
        self.socketio = None
        self.server_thread = None
    
    def create_app(self) -> Flask:
        """创建Flask应用"""
        if not self.app:
            self.app = create_app()
            self.socketio = self.app.socketio
        return self.app
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """运行Web服务器"""
        if not self.app:
            self.create_app()
        
        host = host or config.web_host
        port = port or config.web_port
        debug = debug if debug is not None else config.web_debug
        
        print(f"🌐 启动Web服务器: http://{host}:{port}")
        print(f"🎯 反馈收集: http://{host}:{port}/feedback")
        print(f"🤖 AI聊天: http://{host}:{port}/chat")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)
    
    def run_in_thread(self, host: str = None, port: int = None, debug: bool = False):
        """在后台线程中运行Web服务器"""
        if self.server_thread and self.server_thread.is_alive():
            return

        def _run():
            self.run(host, port, debug)

        self.server_thread = threading.Thread(target=_run, daemon=True)
        self.server_thread.start()

        return self.server_thread

    def collect_feedback(self, work_summary: str, timeout_seconds: int) -> list:
        """收集用户反馈（Web模式）"""
        import time
        import threading

        # 确保Web服务器运行
        if not self.server_thread or not self.server_thread.is_alive():
            self.run_in_thread()
            time.sleep(2)  # 等待服务器启动

        # 构建访问URL
        host = config.web_host
        port = config.web_port
        url = f"http://{host}:{port}/feedback"
        if work_summary:
            import urllib.parse
            url += f"?work_summary={urllib.parse.quote(work_summary)}"

        # 返回提示信息，让用户访问Web界面
        return [{
            "success": True,
            "message": f"Web反馈界面已启动，请在浏览器中访问以下链接提交反馈：",
            "url": url,
            "instructions": [
                "提供文字反馈",
                "上传图片或从剪贴板粘贴图片",
                "与AI助手进行交互式对话"
            ],
            "note": "这个工具非常适合收集用户反馈，问题合并进行交互式对话。请在浏览器中打开上述链接进行操作。"
        }]
