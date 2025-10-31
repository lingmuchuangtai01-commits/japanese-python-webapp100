from flask import Flask, request, render_template_string
import io
import sys
import traceback

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

# --- やさしい日本語エラーメッセージ ---
error_messages = {
    "SyntaxError": "文の書き方が間違っています。\n（例：「かっこ」や「：」を忘れていませんか？）",
    "NameError": "使おうとした名前（変数や関数）が見つかりません。\n（例：「あいさつ」という変数をまだ作っていませんか？）",
    "TypeError": "データの種類（数・文字など）が合っていません。\n（例：「文字」と「数」を足そうとしていませんか？）",
    "ZeroDivisionError": "0で割ることはできません。\n（例：「10 ÷ 0」は計算できません）",
    "IndentationError": "インデント（字下げ）が正しくありません。\n（例：「もし」や「繰り返し」の後にスペースを入れましたか？）",
    "AttributeError": "そのもの（オブジェクト）に使える命令が違います。\n（例：「数字」に対して「追加する」は使えません）",
    "ValueError": "値が正しくありません。\n（例：「数字に変換できない文字」を使っていませんか？）",
    "IndexError": "順番の番号が多すぎます。\n（例：リストの長さより大きい番号を使っていませんか？）",
    "KeyError": "その名前（キー）が見つかりません。\n（例：「辞書」にその言葉が入っていますか？）",
    "RuntimeError": "プログラムの途中で問題が起きました。\n（もう一度ゆっくり確認してみましょう）",
    "ImportError": "読み込もうとしたものが見つかりません。\n（ファイル名やライブラリ名を確認してください）",
}

# --- 日本語→Python変換 ---
def translate(jp_code: str) -> str:
    for jp in sorted(mapping.keys(), key=len, reverse=True):
        jp_code = jp_code.replace(jp, mapping[jp])
    return jp_code

# --- 日本語コード実行 + エラー翻訳 ---
def run_japanese_code(jp_code: str) -> str:
    py_code = translate(jp_code)
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    try:
        exec(py_code, {})
    except Exception as e:
        sys.stdout = sys_stdout
        err_type = type(e).__name__
        jp_message = error_messages.get(err_type, f"不明なエラーが発生しました ({err_type})")
        detail = str(e)
        return f"⚠️ {jp_message}\n\n💬 詳細: {detail}"
    finally:
        sys.stdout = sys_stdout

    return buffer.getvalue()


# --- HTML（スマホ対応＋日本語エラー強調） ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日本語Python - スマホ版</title>
    <style>
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background: linear-gradient(180deg, #f8f9fa, #e9ecef);
            margin: 0;
            padding: 0;
            text-align: center;
        }
        header {
            background: #0078D7;
            color: white;
            padding: 20px 10px;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
        }
        h1 {
            margin: 0;
            font-size: 1.8em;
        }
        p.subtitle {
            margin-top: 6px;
            font-size: 1em;
            color: #e0f7ff;
        }
        form {
            max-width: 90%;
            margin: 20px auto;
            background: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 200px;
            font-size: 16px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-sizing: border-box;
            resize: vertical;
        }
        button {
            width: 100%;
            background-color: #0078D7;
            color: white;
            border: none;
            padding: 12px;
            font-size: 17px;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #005fa3;
        }
        pre {
            text-align: left;
            background: #1e1e1e;
            color: #0f0;
            padding: 12px;
            border-radius: 10px;
            font-family: Consolas, monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: auto;
        }
        .error {
            background: #fff5f5;
            border: 1px solid #ffb3b3;
            color: #cc0000;
            padding: 10px;
            border-radius: 10px;
            margin: 10px auto;
            max-width: 90%;
            font-size: 15px;
            white-space: pre-wrap;
        }
        footer {
            font-size: 0.9em;
            color: #777;
            margin: 30px 0 10px;
        }
        @media (max-width: 480px) {
            h1 { font-size: 1.5em; }
            textarea { height: 180px; font-size: 15px; }
            button { font-size: 16px; }
        }
    </style>
</head>
<body>
    <header>
        <h1>🐍 日本語Python</h1>
        <p class="subtitle">スマホでも使える！やさしいエラー説明つき</p>
    </header>

    <form method="post">
        <textarea name="code" placeholder="ここに日本語Pythonコードを書いてください">{{ code }}</textarea>
        <button type="submit">▶ 実行</button>
    </form>

    {% if result %}
    {% if "⚠️" in result %}
        <div class="error">{{ result }}</div>
    {% else %}
        <h2>🧾 実行結果</h2>
        <pre>{{ result }}</pre>
    {% endif %}
    {% endif %}

    <footer>© 2025 日本語Pythonプロジェクト</footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    result = ""
    if request.method == "POST":
        code = request.form["code"]
        result = run_japanese_code(code)
    return render_template_string(HTML_PAGE, code=code, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
