import os
import sys
import tempfile
import subprocess
import uuid
import queue
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
import shutil
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory, session, current_app
import stat
import time

# 自动切换到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, static_folder='.', static_url_path='')
    app.secret_key = 'your_secret_key_here'
    app.config['UPLOAD_ROOT'] = 'uploads'
    app.config['executor'] = ThreadPoolExecutor(max_workers=8)

    def get_user_dir():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        user_dir = os.path.join(current_app.config['UPLOAD_ROOT'], session['session_id'])
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def handle_error(e, task_id=None, custom_msg=None):
        error_msg = f'{custom_msg if custom_msg else "发生错误"}: {str(e)}'
        if task_id:
            logger.error(f'Task {task_id} error: {error_msg}')
        else:
            logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

    def on_rm_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')

    @app.route('/run_code', methods=['POST'])
    def run_code():
        try:
            code = request.json.get('code')
            if not code:
                return handle_error(ValueError('No code provided'), custom_msg='未提供代码'), 400

            task_id = str(uuid.uuid4())
            logger.info(f'Starting task {task_id}')

            temp_dir = tempfile.mkdtemp(dir=current_app.config['UPLOAD_ROOT'])
            temp_file = os.path.join(temp_dir, 'user_code.py')

            # 写入代码到临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)

            # 复制数据集到临时目录
            user_dir = get_user_dir()
            for fname in os.listdir(user_dir):
                if fname.lower().endswith('.csv'):
                    shutil.copy2(
                        os.path.join(user_dir, fname),
                        os.path.join(temp_dir, fname)
                    )

            result_queue = queue.Queue()

            def run_in_thread():
                try:
                    result = subprocess.run(
                        [sys.executable, 'user_code.py'],
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,
                        timeout=30
                    )

                    if result.returncode == 0:
                        result_queue.put({'success': True, 'output': result.stdout})
                    else:
                        result_queue.put({
                            'success': False,
                            'error': f'代码执行失败 (返回码: {result.returncode}):\n{result.stderr}'
                        })
                except subprocess.TimeoutExpired:
                    result_queue.put({'success': False, 'error': '代码执行超时（30秒）'})
                except Exception as e:
                    result_queue.put({
                        'success': False,
                        'error': f'执行代码时发生错误:\n{str(e)}\n\n详细错误信息:\n{traceback.format_exc()}'
                    })

            current_app.config['executor'].submit(run_in_thread)

            try:
                result = result_queue.get(timeout=35)

                # 复制模型文件
                user_dir = get_user_dir()
                for fname in os.listdir(temp_dir):
                    if fname.lower().endswith('.pkl'):
                        shutil.copy2(
                            os.path.join(temp_dir, fname),
                            os.path.join(user_dir, fname)
                        )

                return jsonify(result)
            except queue.Empty:
                return handle_error(TimeoutError('执行超时（35秒）'), task_id)

        except Exception as e:
            return handle_error(e, task_id)
        finally:
            # 确保所有操作完成后再删除临时目录，增强健壮性
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                time.sleep(0.1)  # 等待文件释放
                shutil.rmtree(temp_dir, onerror=on_rm_error)

    @app.route('/download_model', methods=['GET'])
    def download_model():
        try:
            model_name = request.args.get('model_name')
            if not model_name:
                return handle_error(ValueError('No model name provided'), custom_msg='未提供模型名称'), 400

            model_path = os.path.join(get_user_dir(), f'{model_name}.pkl')
            if not os.path.exists(model_path):
                return handle_error(FileNotFoundError('Model file not found'), custom_msg='模型文件未找到'), 404

            return send_file(model_path, as_attachment=True, download_name=f'{model_name}.pkl')
        except Exception as e:
            return handle_error(e)

    @app.route('/upload_dataset', methods=['POST'])
    def upload_dataset():
        try:
            if 'file' not in request.files:
                return handle_error(ValueError('No file part'), custom_msg='未提供文件')

            file = request.files['file']
            if file.filename == '':
                return handle_error(ValueError('No selected file'), custom_msg='未选择文件')

            filename = secure_filename(file.filename)
            save_path = os.path.join(get_user_dir(), filename)
            file.save(save_path)

            # 处理文件编码
            try:
                with open(save_path, 'rb') as f:
                    content = f.read()
                try:
                    content.decode('utf-8')
                except UnicodeDecodeError:
                    content = content.decode('gbk').encode('utf-8')
                    with open(save_path, 'wb') as f:
                        f.write(content)
            except Exception as e:
                return handle_error(e, custom_msg='请检查文件编码')

            # 读取CSV信息
            import csv
            with open(save_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                col_names = next(reader, [])
                col_count = len(col_names)

            return jsonify({
                'success': True,
                'filename': filename,
                'col_count': col_count,
                'col_names': col_names
            })
        except Exception as e:
            return handle_error(e)

    return app

def run(host='0.0.0.0', port=5000, debug=True, **kwargs):
    app = create_app()
    os.makedirs(app.config.get('UPLOAD_ROOT', 'uploads'), exist_ok=True)
    app.run(host=host, port=port, debug=debug, **kwargs)

if __name__ == '__main__':
    run(port=5001)
