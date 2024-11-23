# P5 Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle Colabでp5.js/q5.js/p5play.jsを使ったコードセルのPythonコードをPyScriptを使ってiframe(ブラウザ)上で実行するマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install -q -U pysmagic p5magic
from p5magic import register_p5magic

register_p5magic()
```

### マジックコマンドの使い方

コードセルの冒頭に以下のようにマジックコマンドを記述してください。実行するとアウトプットにiframeが表示されてその中でコードセルのコードがPyScriptで実行されます。グローバルモード及びインスタンスモードの両方に対応しています。

以下は、q5.jsライブラリを使って描画した赤い円を矢印キーで動かす例です。

#### グローバルモード

```python
%%runp5

x = 100
y = 100

def setup():
    p5.createCanvas(300, 300)

def draw():
    global x, y
    background(128)
    fill(255, 0, 0)
    ellipse(x, y, 50, 50)

    if keyIsDown(LEFT_ARROW):
        x -= 1
    if keyIsDown(RIGHT_ARROW):
        x += 1
    if keyIsDown(UP_ARROW):
        y -= 1
    if keyIsDown(DOWN_ARROW):
        y += 1
```

#### インスタンスモード

```python
%%runp5 500 500 white '{}' False

import pyscript
import js

def sketch(p5):
    x = 100
    y = 100

    def setup():
        p5.createCanvas(300, 300)

    def draw():
        nonlocal x, y
        p5.background(128)
        p5.fill(255, 0, 0)
        p5.ellipse(x, y, 50, 50)

        if p5.keyIsDown(p5.LEFT_ARROW):
            x -= 1
        if p5.keyIsDown(p5.RIGHT_ARROW):
            x += 1
        if p5.keyIsDown(p5.UP_ARROW):
            y -= 1
        if p5.keyIsDown(p5.DOWN_ARROW):
            y += 1

    p5.setup = setup
    p5.draw = draw

js.p5start(sketch)
```

### グローバル変数

PyScriptから以下の変数にアクセスできます。

- 別のセルで設定したグローバル変数(_で始まる変数名やJSONに変換できないものは除く)
- マジックコマンドの引数py_valで設定した変数
- width: iframeの幅(マジックコマンドの引数で指定した幅)
- height: iframeの高さ(マジックコマンドの引数で指定した高さ)

この変数はjs.pysオブジェクトを介してアクセスできます。
変数名が衝突した場合は上記リストの順に上書きされて適用されます。

### マジックコマンド

#### %%runp5

セル内のp5play.jsライブラリを使ったPythonコードをPyScriptを用いてiframe内で実行するマジックコマンド

```juypyter
%%runp5 [width] [height] [background] [py_val] [p5_global] [p5_type] [p5play_use] [py_type] [py_conf] [js_src] [py_ver]
```

- width: iframeの幅を指定します。デフォルトは500です。
- height: iframeの高さを指定します。デフォルトは500です。
- background: iframeの背景色を指定します。デフォルトはwhiteです。
- py_val: PyScriptの変数を''で囲んだJSON形式で指定します。デフォルトは'{}'です。
- p5_global: p5playをグローバルモードと同様のコーディングができるようにするかどうかを指定します。デフォルトはTrueです。
- p5_type: 実行するp5.jsの種類。q5またはp5を指定します。q5は軽量p5互換ライブラリのq5.js、p5はp5.jsを使います。デフォルトはq5です。
- p5play_use: p5play.jsを使うかどうかを指定します。デフォルトはFalseです。
- py_type: 実行するPythonの種類。pyまたはmpyを指定します。mpyはMicroPyton、pyはCPython互換のPyodideで実行します。デフォルトはmpyです。グローバルモードのときはmpy固定です。
- py_conf: PyScriptの設定を''で囲んだJSON形式で指定します。デフォルトは'{}'です。
- js_src: 外部JavaScriptのURLを''で囲んだ文字列のJSON配列形式で指定します。デフォルトは'[]'です。
- py_ver: PyScriptのバージョンを指定します。

#### %%genp5

セル内のp5play.jsライブラリを使ったPythonコードからブラウザで実行可能な単一HTMLを生成するマジックコマンド。オプションはrunp5と同じです。

```juypyter
%%genp5 [width] [height] [background] [p5_global] [p5_type] [p5play_use] [py_type] [py_conf] [js_src] [version]
```

### ライセンス

p5play.jsはAGPL-v3ライセンス・商用ライセンスのデュアルライセンスとなっていますので使用の際は確認してください。
