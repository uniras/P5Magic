# P5 Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle Colabでp5play.jsを使ったコードセルのPythonコードをPyScriptを使ってiframe(ブラウザ)上で実行するマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install -q p5magic
from p5magic import register_p5magic

register_p5magic()
```

### マジックコマンドの使い方

コードセルの冒頭に以下のようにマジックコマンドを記述してください。実行するとアウトプットにiframeが表示されてその中でコードセルのコードがPyScriptで実行されます。グローバルモード及びインスタンスモードの両方に対応しています。

以下は、p5play.jsライブラリを使って描画した赤い円を矢印キーで動かす例です。

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
%%runp5 500 500 white False

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

### マジックコマンド

#### %%runp5

セル内のp5play.jsライブラリを使ったPythonコードをPyScriptを用いてiframe内で実行するマジックコマンド

```juypyter
%%runp5 [width] [height] [background] [p5_global] [p5_type] [py_type] [py_conf] [js_src] [version]
```

- width: iframeの幅を指定します。デフォルトは500です。
- height: iframeの高さを指定します。デフォルトは500です。
- background: iframeの背景色を指定します。デフォルトはwhiteです。
- p5_global: p5playをグローバルモードと同様のコーディングができるようにするかどうかを指定します。デフォルトはTrueです。
- p5_type: 実行するp5.jsの種類。q5またはp5を指定します。q5は軽量p5互換ライブラリのq5.js、p5はp5.jsを使います。デフォルトはq5です。
- py_type: 実行するPythonの種類。pyまたはmpyを指定します。mpyはMicroPyton、pyはCPython互換のPyodideで実行します。デフォルトはmpyです。グローバルモードのときはmpy固定です。
- py_conf: PyScriptの設定を''で囲んだJSON形式で指定します。デフォルトは{}です。
- js_src: 外部JavaScriptのURLを''で囲んだ文字列のJSON配列形式で指定します。デフォルトは[]です。
- version: PyScriptのバージョンを指定します.

#### %%genp5

セル内のp5play.jsライブラリを使ったPythonコードからブラウザで実行可能な単一HTMLを生成するマジックコマンド。オプションはrunp5と同じです。

```juypyter
%%genp5 [width] [height] [background] [p5_global] [p5_type] [py_type] [py_conf] [js_src] [version]
```
