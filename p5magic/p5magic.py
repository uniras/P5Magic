import shlex
import pysmagic
import IPython.core.magic as magic  # type: ignore  # noqa: F401


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
        %%runp5 [width] [height] [background] [p5_global] [p5_type] [p5play_use] [py_type] [py_conf] [js_src] [py_ver]

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
        py_ver: PyScriptのバージョンを指定します.
    """
    args = parse_p5_args(line, cell)
    args["htmlmode"] = False

    pysmagic.run_pyscript(args)


@magic.register_cell_magic
def genp5(line, cell):
    """
    セル内のp5.js/q5.js/p5play.jsライブラリを使ったPythonコードをPyScriptを用いてiframe内で実行するために生成したHTMLを表示するマジックコマンド
    """
    args = parse_p5_args(line, cell)
    args["htmlmode"] = True

    pysmagic.run_pyscript(args)


def parse_p5_args(line, cell):
    # 引数のパース
    line_args = shlex.split(line)
    args = {}
    args["width"] = line_args[0] if len(line_args) > 0 else "500"
    args["height"] = line_args[1] if len(line_args) > 1 else "500"
    args["background"] = line_args[2] if len(line_args) > 2 else "white"
    p5_global = line_args[3].lower() if len(line_args) > 3 else "true"
    p5_type = line_args[4].lower() if len(line_args) > 4 else "q5"
    p5play_use = line_args[5].lower() if len(line_args) > 5 else "false"
    args["py_type"] = line_args[6].lower() if len(line_args) > 6 else "mpy"
    args["py_conf"] = line_args[7] if len(line_args) > 7 and line_args[7] != "{}" else None
    args["js_src"] = line_args[8] if len(line_args) > 8 and line_args[8] != "[]" else None
    args["py_ver"] = line_args[9] if len(line_args) > 9 and line_args[9].lower() != "none" else None

    if p5_type != "p5" and p5_type != "q5":
        raise ValueError("Invalid p5_type. Use p5 or q5")

    # p5.jsのライブラリを選択
    if p5_type == "p5":
        p5lib = ["https://cdn.jsdelivr.net/npm/p5@1/lib/p5.min.js", "https://cdn.jsdelivr.net/npm/p5@1/lib/addons/p5.sound.min.js"]
    else:
        p5lib = ["https://cdn.jsdelivr.net/npm/q5@2/q5.min.js"]

    # p5play.jsを使う場合はライブラリを追加
    if p5play_use == "true":
        p5lib.append("https://cdn.jsdelivr.net/npm/p5play@3/planck.min.js")
        p5lib.append("https://cdn.jsdelivr.net/npm/p5play@3/p5play.js")

    args["add_src"] = p5lib

    args["add_script"] = """
        window.p5start = (func) => {
            if (typeof window.Q5 !== 'undefined') {
                new Q5(func);
            } else {
                new p5(func);
            }
        }
"""

    # 追加cssの設定
    args["add_style"] = """
        html,
        body {
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }

        canvas {
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
        }
"""

    # グローバルモードのコードを生成
    if p5_global == "true":
        args["py_type"] = "mpy"
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

js.p5start(_p5_global)
"""
    else:
        p5globalCode = ""

    args["py_script"] = cell + p5globalCode

    return args
