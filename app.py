from flask import Flask, request, render_template_string
import io
import sys

app = Flask(__name__)

# --- 日本語→Python変換マップ ---
mapping = {
    "表示": "print",
    "入力": "input",
    "範囲": "range",
    "長さ": "len",
    "型": "type",
    "もし": "if",
    "でなければ": "else",
    "繰り返し": "for",
    "範囲内で": "in",
    "関数": "def",
    "戻す": "return",
    "クラス": "class",
    "継承": "super",
    "試す": "try",
    "失敗なら": "except",
    "続ける": "continue",
    "抜ける": "break",
    "かつ": "and",
    "または": "or",
    "ではない": "not",
    "真": "True",
    "偽": "False",
    "無": "None"
}

# --- 日本語コードをPythonに変換 ---
def translate(jp_code: str) -> str:
    for jp in sorted(mapping.keys(), key=len, reverse=True):
        jp_code = jp_code.replace(jp, mapping[jp])
    return jp_code

# --- 日本語コードを実行 ---
def run_japanese_code(jp_code: str) -> str:
    py_code = translate(jp_code)
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    try:
        exec(py_code, {})
    except Exception as e:
        return f"エラー: {e}"
    finally:
        sys.stdout = sys_stdout

    return buffer.getvalue()


# --- トップページ ---
HOME_PAGE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>日本語Python ホーム</title>
    <style>
        body {
            text-align: center;
            font-family: "Segoe UI", sans-serif;
            background-color: #f7f7ff;
            padding-top: 100px;
        }
        h1 {
            color: #333;
        }
        .button {
            display: inline-block;
            margin-top: 40px;
            background-color: #4CAF50;
            color: white;
            padding: 15px 25px;
            text-decoration: none;
            border-radius: 8px;
            font-size: 18px;
            transition: 0.3s;
        }
        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>🐍 日本語Python ホーム</h1>
    <p>日本語で書いたPythonコードを実行できるページへ進めます。</p>
    <a href="/run" class="button">日本語プログラミングページへ ▶</a>
</body>
</html>
"""

# --- 日本語Python 実行ページ ---
RUN_PAGE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日本語Python 実行アプリ</title>
    <style>
        body {
            font-family: "Segoe UI", sans-serif;
            background: #f8f9fa;
            padding: 15px;
            margin: 0;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        form {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 220px;
            font-size: 16px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            resize: vertical;
        }
        button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        pre {
            background: #222;
            color: #0f0;
            padding: 12px;
            border-radius: 8px;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: auto;
            font-family: Consolas, monospace;
        }
        h2 {
            text-align: center;
        }
        a.back {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #007BFF;
            text-decoration: none;
        }
        a.back:hover {
            text-decoration: underline;
        }
        @media (max-width: 480px) {
            textarea {
                height: 180px;
                font-size: 15px;
            }
            button {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <h1>🐍 日本語Python 実行アプリ</h1>
    <form method="post">
        <textarea name="code" placeholder="ここに日本語Pythonコードを書いてください">{{ code }}</textarea>
        <button type="submit">▶ 実行</button>
    </form>
    <h2>🧾 結果</h2>
    <pre>{{ result }}</pre>
    <a href="/" class="back">← ホームに戻る</a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_PAGE)

@app.route("/run", methods=["GET", "POST"])
def run_page():
    code = ""
    result = ""
    if request.method == "POST":
        code = request.form["code"]
        result = run_japanese_code(code)
    return render_template_string(RUN_PAGE, code=code, result=result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
