import shlex
import tempfile
import os
import socket
import threading
import time
import subprocess
import json
import IPython.core.magic as magic  # type: ignore  # noqa: F401
import IPython.display as display  # type: ignore  # noqa: F401


PYS_DEFAULT_VERSION = "2024.10.1"


# Google Colabで実行しているかどうかを判定
def is_google_colab():
    try:
        import google.colab  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


# ベースディレクトリを取得
def get_basedir():
    if is_google_colab():
        if os.path.exists("/content/drive/MyDrive"):
            return "/content/drive/MyDrive/Colab Notebooks"
        else:
            return "/content"
    else:
        return os.getcwd()


# magic commandを登録する関数
def register_p5magic():
    from IPython import get_ipython  # type: ignore  # noqa: F401
    ipy = get_ipython()
    ipy.register_magic_function(runp5)
    ipy.register_magic_function(genp5)
    print("Registered PyScript magic commands.")


# iframe内でPyScriptを実行するマジックコマンド
@magic.register_cell_magic
def runp5(line, cell):
    """
    セル内のp5.js/q5.js/p5play.jsライブラリを使ったPythonコードをPyScriptを用いてiframe内で実行するマジックコマンド

    Usage:
        %%runp5 [width] [height] [background] [p5_global] [p5_type] [p5_conf] [p5play_use] [py_type] [py_conf] [js_src] [version]

    Args:
        width: iframeの幅を指定します。デフォルトは500です。
        height: iframeの高さを指定します。デフォルトは500です。
        background: iframeの背景色を指定します。デフォルトはwhiteです。
        p5_global: p5をグローバルモードと同様のコーディングができるようにするかどうかを指定します。デフォルトはTrueです。
        p5_type: 実行するp5.jsの種類。q5またはp5を指定します。q5は軽量p5互換ライブラリのq5.js、p5はp5.jsを使います。デフォルトはq5です。
        p5play_use: p5play.jsを使用するかどうかを指定します。デフォルトはFalseです。
        py_type: 実行するPythonの種類。pyまたはmpyを指定します。mpyはMicroPyton、pyはCPython互換のPyodideで実行します。デフォルトはmpyです。グローバルモードのときはmpy固定です。
        py_conf: PyScriptの設定を''で囲んだJSON形式で指定します。デフォルトは{}です。
        js_src: 外部JavaScriptのURLを''で囲んだ文字列のJSON配列形式で指定します。デフォルトは[]です。
        version: PyScriptのバージョンを指定します.
    """
    p5_execute(line, cell, False)


@magic.register_cell_magic
def genp5(line, cell):
    """
    セル内のp5.js/q5.js/p5play.jsライブラリを使ったPythonコードをPyScriptを用いてiframe内で実行するために生成したHTMLを表示するマジックコマンド
    """
    p5_execute(line, cell, True)


def p5_execute(line, cell, viewmode):
    # 引数のパース
    args = shlex.split(line)
    width = int(args[0]) if len(args) > 0 else 500
    height = int(args[1]) if len(args) > 1 else 500
    background = args[2] if len(args) > 2 else "white"
    p5_global = args[3] if len(args) > 3 else "True"
    p5_type = args[4] if len(args) > 4 else "q5"
    p5play_use = args[5] if len(args) > 5 else "False"
    py_type = args[6] if len(args) > 6 else "mpy"
    py_conf = args[7] if len(args) > 7 and args[4] != "{}" else None
    js_src = args[8] if len(args) > 8 and args[5] != "[]" else None
    version = args[9] if len(args) > 9 else PYS_DEFAULT_VERSION

    if py_type != "py" and py_type != "mpy":
        raise ValueError("Invalid type. Use py or mpy")

    if p5_type != "p5" and p5_type != "q5":
        raise ValueError("Invalid p5_type. Use p5 or q5")

    # p5.jsのライブラリを選択
    if p5_type == "p5":
        p5lib = ["https://cdn.jsdelivr.net/npm/p5@1/lib/p5.min.js"]
    else:
        p5lib = ["https://cdn.jsdelivr.net/npm/q5@2/q5.min.js"]

    # p5play.jsを使う場合はライブラリを追加
    if p5play_use == "True" or p5play_use == "true":
        p5lib.append("https://cdn.jsdelivr.net/npm/p5play@3/planck.min.js")
        p5lib.append("https://cdn.jsdelivr.net/npm/p5play@3/p5play.js")

    # p5.jsのライブラリ要素を生成
    p5libtag = "\n".join([f"""    <script src="{lib}"></script>""" for lib in p5lib])
    p5libtag = p5libtag.rstrip("\n")
    p5libtag = f"\n{p5libtag}"

    # グローバルモードのコードを生成
    if p5_global == "True" or p5_global == "true":
        py_type = "mpy"
        p5globalCode = """
import js

p5 = None

def _p5_global(p5instance):
    global p5
    p5 = p5instance

    for name in dir(p5):
        attr = getattr(p5, name)
        if not name.startswith("__"):
            globals()[name] = attr

    p5.setup = setup if 'setup' in globals() else js.undefined
    p5.draw = draw if 'draw' in globals() else js.undefined
    p5.mousePressed = mousePressed if 'mousePressed' in globals() else js.undefined
    p5.mouseReleased = mouseReleased if 'mouseReleased' in globals() else js.undefined
    p5.mouseClicked = mouseClicked if 'mouseClicked' in globals() else js.undefined
    p5.mouseMoved = mouseMoved if 'mouseMoved' in globals() else js.undefined
    p5.mouseDragged = mouseDragged if 'mouseDragged' in globals() else js.undefined
    p5.mouseWheel = mouseWheel if 'mouseWheel' in globals() else js.undefined
    p5.keyPressed = keyPressed if 'keyPressed' in globals() else js.undefined
    p5.keyReleased = keyReleased if 'keyReleased' in globals() else js.undefined
    p5.keyTyped = keyTyped if 'keyTyped' in globals() else js.undefined
    p5.touchStarted = touchStarted if 'touchStarted' in globals() else js.undefined
    p5.touchMoved = touchMoved if 'touchMoved' in globals() else js.undefined
    p5.touchEnded = touchEnded if 'touchEnded' in globals() else js.undefined
    p5.deviceMoved = deviceMoved if 'deviceMoved' in globals() else js.undefined
    p5.deviceTurned = deviceTurned if 'deviceTurned' in globals() else js.undefined
    p5.deviceShaken = deviceShaken if 'deviceShaken' in globals() else js.undefined
    p5.windowResized = windowResized if 'windowResized' in globals() else js.undefined
    p5.preload = preload if 'preload' in globals() else js.undefined
    p5.dragOver = dragOver if 'dragOver' in globals() else js.undefined
    p5.dragLeave = dragLeave if 'dragLeave' in globals() else js.undefined
    p5.drop = drop if 'drop' in globals() else js.undefined

js.window.p5start(_p5_global)

        """.strip()
    else:
        p5globalCode = ""

    # 外部JavaSript要素を生成
    if js_src is not None:
        try:
            srcs = json.loads(js_src)
            if not isinstance(srcs, list):
                raise ValueError("Invalid JSON List format for js_src")
            js_srctag = "\n".join([f"""    <script src="{src}"></script>""" for src in srcs])
            js_srctag = js_srctag.rstrip("\n")
            js_srctag = f"\n{js_srctag}"
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON List format for js_src")
    else:
        js_srctag = ""

    # py-config要素を生成
    if py_conf is not None:
        try:
            json.loads(py_conf)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for py_conf")
        py_config = f"\n    <{py_type}-config>{py_conf}</{py_type}-config>"
    else:
        py_config = ""

    # コードのHTMLテンプレート生成
    base_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script type="module" src="https://pyscript.net/releases/{version}/core.js"></script>{p5libtag}{js_srctag}{py_config}
    <script type="module">
        const loading = document.getElementById('loading');
        addEventListener('{py_type}:ready', () => loading.close());
        loading.showModal();
        window.p5start = (func) => {{
            if (typeof window.Q5 !== 'undefined') {{
                new Q5(func);
            }} else {{
                new p5(func);
            }}
        }}
    </script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://pyscript.net/releases/{version}/core.css" />
    <style>
        html,
        body {{
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }}

        canvas {{
            display: block;
            max-width: 100%;
            max-height: 100vh;
            width: auto;
            height: auto;
            object-fit: cover;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }}
    </style>
</head>
<body style="background:{background};">
    <dialog id="loading" style="outline:none; border:none; background:transparent;">
        <div class="spinner-border" role="status"></div>
        <span class="sr-only">Loading PyScript...</span>
    </dialog>
    <script type="{py_type}">
{cell}
{p5globalCode}
    </script>
</body>
</html>
    """.strip()

    if viewmode:
        # HTMLを表示
        display.display(display.Pretty(base_html))

    else:
        # 一時ファイルを作成
        basedir = get_basedir()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, dir=basedir, encoding="utf-8") as f:
            f.write(base_html)
            temp_html_path = f.name

        # 空いているポート番号を取得
        port = find_free_port()

        # サーバーURLを取得
        url = get_server_url(port)

        # サーバーを起動
        start_server(temp_html_path, port)

        # ファイル名をURLに追加
        htmlurl = url + "/" + os.path.basename(temp_html_path)

        # IFrameを使用して表示
        display.display(display.IFrame(src=htmlurl, width=width, height=height))


# JavaScriptを実行してプロキシURLを取得
def get_server_url(port):
    if is_google_colab():
        from google.colab.output import eval_js  # type: ignore
        url = eval_js(f"google.colab.kernel.proxyPort({port}, {{'cache': true}})").strip("/")
    else:
        url = f"http://localhost:{port}"

    return url


# 18000番台で空いているポート番号を取得
def find_free_port(start=18000, end=18099):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError("No free ports available")


# サーバーの実行
def start_server_func(file_path, port):
    TIMEOUT = 30  # サーバーのタイムアウト（秒）
    server_process = subprocess.Popen(["python", "-m", "http.server", f"{port}"])
    time.sleep(TIMEOUT)
    server_process.terminate()  # プロセスの終了
    os.remove(file_path)


# サーバを別スレッドで起動
def start_server(file_path, port):
    thread = threading.Thread(target=start_server_func, args=(file_path, port))
    thread.daemon = True
    thread.start()
    time.sleep(1)  # サーバーが起動するまで待つ
