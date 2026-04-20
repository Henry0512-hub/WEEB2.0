"""
ACCE v2.0 - Web 后端服务器
提供API接口运行TradingAgents分析
"""

import os
import sys

import json
import math
import queue
import threading
import subprocess
import atexit
import time
import re
from datetime import datetime

from tradingagents.utils.credentials import load_llm_api_keys, load_wrds_credentials
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from flask_sock import Sock

# 必须用脚本所在目录定位 templates/static（避免从别的 cwd 启动时找不到样式）
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(_BASE_DIR, "templates"),
    static_folder=os.path.join(_BASE_DIR, "static"),
    static_url_path="/static",
)
app.config['JSON_AS_ASCII'] = False
# 修改 templates 后尽快生效：Jinja 每次请求重载模板（避免 debug=False 时仍用旧内存模板）
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)
sock = Sock(app)

# 与 TEMPLATES_AUTO_RELOAD 一致，强制 Jinja 从磁盘重载
app.jinja_env.auto_reload = True
app.jinja_env.cache_size = 0


@app.after_request
def _disable_cache_for_page_and_theme_css(response):
    ct = (response.headers.get("Content-Type") or "").lower()
    if request.path == '/' or request.path.endswith('/industrial.css') or 'text/html' in ct:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# 存储客户端连接
clients = []

# 任务缓存（存储AI分析进度）
task_cache = {}
task_lock = threading.Lock()

# 分析任务子进程（退出主进程时终止，避免 Ctrl+C 后子进程仍占用或控制台报错）
_analysis_children_lock = threading.Lock()
_analysis_child_processes = []


def _register_analysis_child(proc):
    with _analysis_children_lock:
        _analysis_child_processes.append(proc)


def _unregister_analysis_child(proc):
    with _analysis_children_lock:
        try:
            _analysis_child_processes.remove(proc)
        except ValueError:
            pass


def _terminate_analysis_children():
    with _analysis_children_lock:
        for p in list(_analysis_child_processes):
            try:
                if p.poll() is None:
                    p.terminate()
            except Exception:
                pass
        _analysis_child_processes.clear()


atexit.register(_terminate_analysis_children)

# 工作目录与 Python 解释器（随项目与运行环境自动确定）
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = sys.executable


class OutputCapture:
    """捕获脚本输出并发送到WebSocket"""

    def __init__(self):
        self.output_queue = queue.Queue()
        self.clients = []

    def add_client(self, client):
        self.clients.append(client)
        print(f"[WebSocket] client connected; count={len(self.clients)}")

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            print(f"[WebSocket] client disconnected; count={len(self.clients)}")

    def broadcast(self, message):
        """广播消息到所有客户端"""
        if not self.clients:
            # 分析完成/进度以 SSE 为主；无 WS 时不刷屏（避免误以为任务失败）
            mtype = message.get("type", "unknown")
            if mtype not in ("complete", "progress"):
                print(f"[WebSocket] warning: no clients; message not sent ({mtype})")
            return

        mtype = message.get("type", "unknown")
        if mtype != "progress":
            print(f"[WebSocket] broadcast to {len(self.clients)} client(s): {mtype}")
        for client in self.clients[:]:
            try:
                client.send(json.dumps(message))
            except Exception as e:
                print(f"[WebSocket] send failed: {e}")
                self.remove_client(client)


output_capture = OutputCapture()

# WebSocket 对 progress 类消息节流（子进程每行 stdout 都会触发；SSE 仍保留全量进度）
_WS_PROGRESS_MIN_INTERVAL_SEC = float(os.environ.get("WS_PROGRESS_INTERVAL", "0.45"))
_last_ws_progress_broadcast_mono = 0.0


def _broadcast_progress_ws_throttled(message: dict) -> None:
    """同一时刻全局限流，避免 2 分钟内 150+ 次 progress 广播刷屏。"""
    global _last_ws_progress_broadcast_mono
    if message.get("type") != "progress":
        output_capture.broadcast(message)
        return
    now = time.monotonic()
    if now - _last_ws_progress_broadcast_mono < _WS_PROGRESS_MIN_INTERVAL_SEC:
        return
    _last_ws_progress_broadcast_mono = now
    output_capture.broadcast(message)


def _json_safe(value):
    """Convert NaN/Inf to None recursively so frontend JSON.parse never fails."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    return value


def _sse_section_for_line(stage, agent_on_line, last_agent, raw_text):
    """
    Track 4: 将每一行流式输出映射到前端分栏。
    - analysis: 分析师、研究员、研究经理、风险辩论等
    - advice: 交易员、投资组合经理、明确评级/推荐类语句
    - skip: 价格数据行等（不进报告栏，由图表管线处理）
    """
    if stage == "price_data":
        return "skip"
    if stage == "recommendation":
        return "advice"
    eff = agent_on_line or last_agent
    if eff in ("交易员", "Trader", "投资组合经理", "Portfolio Manager"):
        return "advice"
    rt = (raw_text or "").strip()
    if len(rt) < 160 and re.search(
        r"^((强烈)?(买入|卖出|持有)|(Buy|Sell|Hold|Overweight|Underweight)\b)", rt, re.I
    ):
        return "advice"
    if re.search(
        r"(最终评级|投资意见|目标价|止损|止盈|"
        r"final rating|investment (view|opinion)|target price|stop[- ]?loss|take[- ]?profit)",
        rt,
        re.I,
    ):
        return "advice"
    return "analysis"


def parse_trading_output(text, last_agent=None):
    """解析TradingAgents输出并转换为结构化数据（含 SSE 分栏 section）。"""
    lines = text.strip().split("\n")
    raw = text.strip()
    if not raw:
        return None

    # 严格真实模式：屏蔽模拟/演示/示例类输出
    lower_raw = raw.lower()
    fake_markers = [
        'mock', 'simulate', 'simulated', 'demo', 'dummy', 'example output',
        '示例', '模拟', '演示', '虚拟', '假设数据'
    ]
    if any(m in lower_raw for m in fake_markers):
        return None

    # 检测当前阶段
    stage = None
    agent = None

    # 检测是否是CSV OHLC数据行（日期开头，包含开高低收数据）
    csv_ohlc_pattern = r'^\d{4}-\d{2}-\d{2},[\d.]+,[\d.]+,[\d.]+,[\d.]+,[\d.]+,'
    if re.match(csv_ohlc_pattern, text.strip()):
        # 这是OHLC数据，需要发送给前端用于绘图
        stage = 'price_data'

    # 只过滤掉纯数据行/超长原始块，保留有意义信息
    skip_patterns = [
        '"fiscalDateEnding"',
        '"reportedCurrency"',
        '"grossProfit"',
        '"totalRevenue"',
        '"costOfRevenue"',
        '"operatingIncome"',
        '"netIncome"',
        '"ebitda"',
        '"ebit"',
        '"interest"',
        '"tax"',
        '"comprehensiveIncome"',
        '"depreciation"',
        'Tool Calls:',
        'Call ID:',
        'Args:',
        'Function:',
        'Thought:',
        'Response:',
        # CSV数据模式（但不包括OHLC数据）
        'Date,Open,High,',
        '## CLOSE_',
        '## RSI',
        '## MACD',
        '## MA_',
        '## VOLUME',
        '## BB_',
        '## STOCH',
        # 警告和错误
        'warnings.warn',
        'rate limited',
        'Warning:',
        'FutureWarning',
        'Deprecated',
        # JSON数据字段
        '"symbol"',
        '"regularMarketPrice"',
        '"previousClose"',
        '"chartPreviousClose"',
        '"currency"',
        '"exchangeName"',
        '"exchangeTimezoneName"',
        '"firstTradeDate"',
        '"priceHint"',
        '"quoteType"',
        '"language"',
        '"region"',
        '"tradeable"',
        '"triggerable"',
        # 技术指标描述
        'Description:',
        'Indicator:',
        'Parameters:',
        # LangChain / 工具噪音
        '==================================',
        'Human Message',
        'Ai Message',
        'Tool Message',
        'Name:',
        # 大块JSON/新闻源字段
        '"feed":',
        '"ticker_sentiment"',
        '"authors":',
        '"banner_image":',
        '"source_domain":',
        '"time_published":',
        '"overall_sentiment_score":',
        '"overall_sentiment_label":',
        '"topic":',
        '"relevance_score":',
        '"url":',
    ]

    # 超长行通常是原始 JSON 或工具回包，直接跳过，避免前端刷屏和卡顿
    if len(raw) > 420:
        return None

    # 噪音JSON片段（单独的 { 或 [ 之类）跳过
    if raw in {'{', '}', '[', ']'}:
        return None

    # 检查是否应该跳过这行（OHLC数据不跳过）
    if stage != 'price_data':
        for pattern in skip_patterns:
            if pattern in text:
                return None  # 返回None表示不广播

    for line in lines:
        if '[' in line and ']' in line:  # 所有的[XXX]格式消息
            stage = 'info'
        elif '推荐' in line and ('买入' in line or '卖出' in line or '持有' in line):
            stage = 'recommendation'
        elif re.search(
            r"(?i)\b(recommendation|rating|investment (view|opinion))\b.*\b("
            r"buy|sell|hold|overweight|underweight|strong\s+buy|strong\s+sell)\b",
            line,
        ):
            stage = 'recommendation'
        elif '市场分析师' in line:
            stage = 'market_analyst'
            agent = '市场分析师'
        elif '社交媒体分析师' in line:
            stage = 'social_analyst'
            agent = '社交媒体分析师'
        elif '新闻分析师' in line:
            stage = 'news_analyst'
            agent = '新闻分析师'
        elif '基本面分析师' in line:
            stage = 'fundamentals_analyst'
            agent = '基本面分析师'
        elif '牛市研究员' in line:
            stage = 'bull_researcher'
            agent = '牛市研究员'
        elif '熊市研究员' in line:
            stage = 'bear_researcher'
            agent = '熊市研究员'
        elif '交易员' in line:
            stage = 'trader'
            agent = '交易员'
        elif '投资组合经理' in line or '最终评级' in line:
            stage = 'portfolio_manager'
            agent = '投资组合经理'
        elif 'Market Analyst' in line:
            stage = 'market_analyst'
            agent = 'Market Analyst'
        elif 'Social Analyst' in line:
            stage = 'social_analyst'
            agent = 'Social Analyst'
        elif 'News Analyst' in line:
            stage = 'news_analyst'
            agent = 'News Analyst'
        elif 'Fundamentals Analyst' in line:
            stage = 'fundamentals_analyst'
            agent = 'Fundamentals Analyst'
        elif 'Bull Researcher' in line:
            stage = 'bull_researcher'
            agent = 'Bull Researcher'
        elif 'Bear Researcher' in line:
            stage = 'bear_researcher'
            agent = 'Bear Researcher'
        elif 'Research Manager' in line:
            stage = 'research_manager'
            agent = 'Research Manager'
        elif 'Portfolio Manager' in line:
            stage = 'portfolio_manager'
            agent = 'Portfolio Manager'
        elif re.search(r'\bTrader\b', line):
            stage = 'trader'
            agent = 'Trader'
        elif 'Aggressive Analyst' in line:
            stage = 'risk'
            agent = 'Aggressive Analyst'
        elif 'Neutral Analyst' in line:
            stage = 'risk'
            agent = 'Neutral Analyst'
        elif 'Conservative Analyst' in line:
            stage = 'risk'
            agent = 'Conservative Analyst'

    section = _sse_section_for_line(stage, agent, last_agent, raw)

    return {
        'text': text,
        'stage': stage,
        'agent': agent,
        'section': section,
        'timestamp': datetime.now().isoformat()
    }


@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')


@app.route('/api/analysts', methods=['GET'])
def get_analysts():
    """获取可用的分析师列表"""
    return jsonify([
        {
            'id': '1',
            'name': 'DeepSeek',
            'description': 'Recommended — low cost (~¥1/M tokens)',
            'icon': '🧠'
        },
        {
            'id': '2',
            'name': 'Kimi',
            'description': '128k context · strong for long documents',
            'icon': '🌙'
        },
        {
            'id': '3',
            'name': 'Gemini',
            'description': 'Google · multimodal reasoning',
            'icon': '⚙'
        }
    ])


@app.route('/api/chart-data', methods=['POST'])
def get_chart_data():
    """
    快速获取图表数据（不依赖AI）
    先返回WRDS数据和技术指标，让用户立即看到图表
    """
    data = request.json
    raw_ticker = (data.get('ticker') or '').strip()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    market_type = (data.get('market_type') or 'us').lower()

    if not raw_ticker or not start_date:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # 导入图表数据模块
        from fast_chart_data import get_wrds_chart_data

        print(f"[chart] {raw_ticker} ({market_type})", flush=True)

        # 获取图表数据（WRDS / efinance / yfinance / 本地库）
        chart_data = get_wrds_chart_data(
            raw_ticker,
            start_date,
            end_date,
            market_type=market_type,
        )

        if chart_data is None:
            return jsonify({
                'status': 'error',
                'message': f'No history for {raw_ticker}: check symbol/market or run python prefetch_ntca.py'
            }), 200

        chart_data = _json_safe(chart_data)

        print(f"[Chart] Successfully got chart data", flush=True)

        return jsonify({
            'status': 'success',
            'data': chart_data,
            'message': 'Chart data ready'
        })

    except Exception as e:
        print(f"[Chart] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """
    启动AI分析任务（后台运行）
    立即返回task_id，AI分析在后台进行
    """
    data = request.json
    print(f"[Analyze] POST /api/analyze", flush=True)

    llm_choice = data.get('llm_choice', '1')
    _raw_ticker = (data.get('ticker') or '').strip()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    analysis_type = data.get('analysis_type', '1')
    market_type = (data.get('market_type') or 'us').lower()
    report_language = (data.get('report_language') or 'en').lower()
    ticker = _raw_ticker.upper() if market_type == 'us' else _raw_ticker

    # 验证输入
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    if not start_date:
        return jsonify({'error': 'Start date is required'}), 400

    # 生成任务ID
    import uuid
    task_id = str(uuid.uuid4())

    # 在后台线程中运行分析
    def run_analysis():
        # 初始化任务缓存
        with task_lock:
            task_cache[task_id] = {
                'status': 'running',
                'progress': [],
                'ticker': ticker,
                'start_time': datetime.now().isoformat()
            }

        try:
            # 使用命令行参数运行脚本
            cmd = [
                PYTHON_PATH,
                os.path.join(WORK_DIR, 'run_analysis_web.py'),
                llm_choice,
                ticker,
                start_date,
                end_date if end_date else 'None',
                analysis_type,
                market_type,
                report_language
            ]

            print(f"[Analyze] [{task_id}] starting subprocess...")
            print(f"[Analyze] [{task_id}] cmd: {' '.join(cmd)}")

            # 子进程继承环境；为避免任何交互式提示，这里显式注入 WRDS_*（若可从 is/wrds.txt 读取）
            child_env = os.environ.copy()
            wrds_creds = load_wrds_credentials()
            if wrds_creds:
                child_env["WRDS_USERNAME"] = wrds_creds["username"]
                child_env["WRDS_PASSWORD"] = wrds_creds["password"]
                print(f"[Analyze] [{task_id}] WRDS credentials loaded (is/wrds.txt / env)")
            else:
                print(f"[Analyze] [{task_id}] no WRDS credentials (is/wrds.txt / env)")

            # 强制从 is/api assents.txt 读取 LLM key，注入子进程环境，避免连接时缺失
            llm_keys = load_llm_api_keys() or {}
            ds = (llm_keys.get("deepseek") or "").strip()
            km = (llm_keys.get("kimi") or "").strip()
            gm = (llm_keys.get("gemini") or "").strip()
            if ds:
                child_env["DEEPSEEK_API_KEY"] = ds
                child_env["OPENAI_API_KEY"] = ds
            if km:
                child_env["KIMI_API_KEY"] = km
                child_env["MOONSHOT_API_KEY"] = km
            if gm:
                child_env["GEMINI_API_KEY"] = gm
                child_env["GOOGLE_API_KEY"] = gm
            print(f"[Analyze] [{task_id}] injected LLM keys (deepseek={bool(ds)}, kimi={bool(km)}, gemini={bool(gm)})")
            child_env.setdefault("ANALYSIS_LLM_TIMEOUT_SEC", "90")
            child_env.setdefault("ANALYSIS_LLM_MAX_RETRIES", "1")
            child_env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                cmd,
                cwd=WORK_DIR,
                env=child_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
            )

            print(f"[Analyze] [{task_id}] subprocess PID: {process.pid}")

            _register_analysis_child(process)

            stdout_lines: list[str] = []
            last_agent_holder: list = [None]

            def _append_progress_item(item: dict) -> None:
                with task_lock:
                    if task_id not in task_cache:
                        return
                    task_cache[task_id].setdefault("progress", []).append(item)

            def _drain_stdout() -> None:
                try:
                    if process.stdout is None:
                        return
                    for raw in iter(process.stdout.readline, ""):
                        stdout_lines.append(raw)
                        line = raw.rstrip("\r\n")
                        if not line:
                            continue
                        parsed = parse_trading_output(line, last_agent_holder[0])
                        if parsed:
                            la = parsed.get("agent")
                            if la:
                                last_agent_holder[0] = la
                            _append_progress_item(parsed)
                except Exception as exc:
                    print(f"[Analyze] [{task_id}] stdout reader: {exc}", flush=True)

            drain_thread = threading.Thread(target=_drain_stdout, daemon=True)
            drain_thread.start()

            stop_heartbeat = threading.Event()

            def _heartbeat_loop() -> None:
                """So the UI/SSE are not silent for many minutes during long graph runs."""
                first_wait = True
                while True:
                    delay_sec = 25.0 if first_wait else 45.0
                    first_wait = False
                    if stop_heartbeat.wait(delay_sec):
                        break
                    if process.poll() is not None:
                        break
                    _append_progress_item({
                        'text': (
                            '[Status] Still running — full multi-agent analysis often needs 3–15+ minutes. '
                            'If you want a faster run, set environment variable ACCE_DIRECT_LLM_ONLY=1 '
                            'and restart the web server.'
                        ),
                        'stage': 'heartbeat',
                        'agent': None,
                        'section': 'analysis',
                        'timestamp': datetime.now().isoformat(),
                    })
                    try:
                        _broadcast_progress_ws_throttled({
                            'type': 'progress',
                            'task_id': task_id,
                            'data': {'text': '[Status] Still running (LLM / agents)…', 'agent': None},
                        })
                    except Exception:
                        pass

            hb_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
            hb_thread.start()

            return_code = None
            process_timeout_sec = int(os.environ.get("ANALYSIS_PROCESS_TIMEOUT_SEC", "3600"))
            try:
                return_code = process.wait(timeout=process_timeout_sec)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except Exception:
                    pass
                try:
                    process.wait(timeout=25)
                except Exception:
                    pass
                with task_lock:
                    if task_id in task_cache:
                        task_cache[task_id]['status'] = 'timeout'
                        task_cache[task_id]['error'] = f'Analysis timed out (>{process_timeout_sec}s)'
                        task_cache[task_id]['end_time'] = datetime.now().isoformat()
                output_capture.broadcast({
                    'type': 'error',
                    'task_id': task_id,
                    'message': f'Analysis timed out (>{process_timeout_sec}s)'
                })
                return
            finally:
                stop_heartbeat.set()
                try:
                    hb_thread.join(timeout=3)
                except Exception:
                    pass
                try:
                    if process.stdout:
                        process.stdout.close()
                except Exception:
                    pass
                drain_thread.join(timeout=15)
                _unregister_analysis_child(process)

            line_count = len(stdout_lines)
            print(f"[Analyze] [{task_id}] done, exit={return_code}, lines={line_count}")

            full_text = "".join(stdout_lines)
            report_blob = {
                'text': full_text,
                'stage': 'complete_output',
                'report_only': True,
                'section': 'analysis',
                'timestamp': datetime.now().isoformat()
            }

            with task_lock:
                if task_id in task_cache:
                    task_cache[task_id]['status'] = 'completed'
                    task_cache[task_id]['return_code'] = return_code
                    task_cache[task_id]['end_time'] = datetime.now().isoformat()
                    task_cache[task_id].setdefault('progress', []).append(report_blob)

            # 发送完成消息（不推送逐行 progress）
            output_capture.broadcast({
                'type': 'complete',
                'task_id': task_id,
                'message': 'Analysis complete',
                'return_code': return_code
            })

        except subprocess.TimeoutExpired:
            with task_lock:
                if task_id in task_cache:
                    task_cache[task_id]['status'] = 'timeout'
                    task_cache[task_id]['error'] = 'Analysis timed out'

            output_capture.broadcast({
                'type': 'error',
                'task_id': task_id,
                'message': 'Analysis timed out'
            })
        except Exception as e:
            with task_lock:
                if task_id in task_cache:
                    task_cache[task_id]['status'] = 'error'
                    task_cache[task_id]['error'] = str(e)

            output_capture.broadcast({
                'type': 'error',
                'task_id': task_id,
                'message': str(e)
            })

    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()

    # 立即返回task_id，不等待分析完成
    return jsonify({
        'status': 'started',
        'task_id': task_id,
        'message': 'Analysis started in background',
        'ticker': ticker
    })


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态和进度"""
    with task_lock:
        task = task_cache.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({
        'task_id': task_id,
        'status': task.get('status'),
        'ticker': task.get('ticker'),
        'start_time': task.get('start_time'),
        'end_time': task.get('end_time'),
        'progress_count': len(task.get('progress', [])),
        'error': task.get('error')
    })


@app.route('/api/task/<task_id>/result', methods=['GET'])
def get_task_result(task_id):
    """获取任务最终文本结果（SSE 失败时前端兜底拉取）"""
    with task_lock:
        task = task_cache.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    progress = task.get('progress') or []
    final_text = ""
    if progress:
        for item in reversed(progress):
            if item.get('stage') == 'complete_output' or item.get('report_only'):
                final_text = item.get('text') or ''
                break
        if not final_text:
            final_text = progress[-1].get('text') or ''

    return jsonify({
        'task_id': task_id,
        'status': task.get('status'),
        'return_code': task.get('return_code'),
        'text': final_text,
        'error': task.get('error')
    })


@app.route('/api/task/<task_id>/progress', methods=['GET'])
def get_task_progress(task_id):
    """获取任务的详细进度（SSE流式传输）"""
    @stream_with_context
    def generate():
        last_index = 0

        while True:
            with task_lock:
                task = task_cache.get(task_id)
                if not task:
                    yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                    return
                progress_list = list(task.get('progress') or [])
                status = task.get('status')
                nprog = len(progress_list)
                pending = progress_list[last_index:nprog] if nprog > last_index else []

            for progress_item in pending:
                try:
                    safe_item = _json_safe(progress_item)
                    yield f"data: {json.dumps(safe_item, ensure_ascii=False)}\n\n"
                except (TypeError, ValueError) as exc:
                    yield f"data: {json.dumps({'error': 'Progress serialization failed', 'detail': str(exc)}, ensure_ascii=False)}\n\n"
                    return
            last_index += len(pending)

            if status in ('completed', 'error', 'timeout'):
                yield f"data: {json.dumps({'type': 'done', 'status': status}, ensure_ascii=False)}\n\n"
                return

            time.sleep(0.5)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )


@sock.route('/ws')
def websocket_connection(ws):
    """WebSocket连接"""
    print(f"[WebSocket] new connection")
    clients.append(ws)
    output_capture.add_client(ws)

    # 发送欢迎消息
    try:
        ws.send(json.dumps({'type': 'connected', 'message': 'WebSocket connected'}))
    except Exception as e:
        print(f"[WebSocket] welcome send failed: {e}")

    try:
        while True:
            data = ws.receive()
            print(f"[WebSocket] client message: {data}")
    except Exception as e:
        print(f"[WebSocket] connection error: {e}")
    finally:
        output_capture.remove_client(ws)
        if ws in clients:
            clients.remove(ws)


if __name__ == '__main__':
    print("=" * 80)
    print(" " * 20 + "ACCE v2.0 - Web server")
    print("=" * 80)
    print()
    print("Starting server...")
    print("Open: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop.")
    print("Tip: After editing templates/index.html, hard-refresh the browser (Ctrl+F5).")
    print("     Set NTCA_DEV=1 for Flask debug + auto-reload.")
    print("=" * 80)
    print()

    _dev = os.environ.get("NTCA_DEV", "").strip().lower() in ("1", "true", "yes", "on")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=_dev,
        use_reloader=_dev,
    )
