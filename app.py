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

# --- 各命令の説明 ---
descriptions = {
    "表示": "画面に文字や数字を出します。",
    "入力": "ユーザーから文字や数字を入力します。",
    "範囲": "0から指定した数までの数を作ります。",
    "長さ": "リストや文字の長さ（数）を調べます。",
    "型": "データの種類（数・文字など）を調べます。",
    "もし": "条件によって動きを分けます。",
    "でなければ": "条件がちがうときに使います。",
    "繰り返し": "同じことを何回も行います。",
    "範囲内で": "リストや数字の中で順番に取り出します。",
    "関数": "動きをまとめるときに使います。",
    "戻す": "関数から値を返します。",
    "クラス": "もの（オブジェクト）の設計図を作ります。",
    "継承": "もとのクラスの動きを引き継ぎます。",
    "試す": "エラーが出るかもしれない部分を試します。",
    "失敗なら": "エラーが出たときの処理を書きます。",
    "続ける": "次のくり返しへ進みます。",
    "抜ける": "くり返しをやめます。",
    "かつ": "両方の条件が正しいときにTrueになります。",
    "または": "どちらかが正しいとTrueになります。",
    "ではない": "反対の意味になります。",
    "真": "はい（True）を表します。",
    "偽": "いいえ（False）を表します。",
    "無": "なにもない（None）を表します。"
}

# --- エラー翻訳 ---
error_messages = {
    "SyntaxError": "文の書き方が間違っています。\n（例：「かっこ」や「：」を忘れていませんか？）",
    "NameError": "使おうとした名前（変数や関数）が見つかりません。\n（例：「あいさつ」という変数をまだ作っていませんか？）",
    "TypeError": "データの種類（数・文字など）が合っていません。\n（例：「文字」と「数」を足そうとしていませんか？）",
    "ZeroDivisionError": "0で割ることはできません。\n（例：「10 ÷ 0」は計算できません）",
    "IndentationError": "インデント（字下げ）が正しくありません。\n（例：「もし」や「繰り返し」の後にスペースを入れましたか？）",
    "AttributeError": "そのものに使える命令が違います。\n（例：「数字」に対して「追加する」は使えません）",
    "ValueError": "値が正しくありません。\n（例：「数字に変換できない文字」を使っていませんか？）",
    "IndexError": "番号が多すぎます。\n（例：リストの長さより大きい番号を使っていませんか？）",
    "KeyError": "その名前（キー）が見つかりません。\n（例：「辞書」にその言葉が入っていますか？）",
    "RuntimeError": "途中で問題が起きました。\n（もう一度ゆっくり確認してみましょう）",
    "ImportError": "読み込もうとしたものが見つかりません。\n（ファイル名やライブラリ名を確認してください）",
}

# --- 翻訳 ---
def translate(jp_code: str) -> str:
    for jp in sorted(mapping.keys(), key=len, reverse=True):
        jp_code = jp_code.replace(jp, mapping[jp])
    return jp_code

# --- 実行 ---
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


# --- メインページ（実行画面） ---
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日本語Python</title>
    <style>
        body { font-family: 'Noto Sans JP', sans-serif; background: #f7f8fa; text-align: center; margin: 0; }
        header { background: #0078D7; color: white; padding: 15px; }
        a { color: white; text-decoration: none; }
        textarea { width: 90%; height: 200px; border-radius: 10px; padding: 10px; margin-top: 10px; font-size: 16px; }
        button { background: #0078D7; color: white; border: none; padding: 10px 20px; border-radius: 10px; font-size: 18px; margin-top: 10px; }
        pre { text-align: left; background: #222; color: #0f0; padding: 12px; border-radius: 10px; margin: 20px auto; width: 90%; }
        .error { background: #fff5f5; color: #cc0000; border: 1px solid #ffb3b3; padding: 10px; border-radius: 10px; width: 90%; margin: 20px auto; white-space: pre-wrap; }
    </style>
</head>
<body>
    <header>
        <h1>🐍 日本語Python</h1>
        <a href="/words">📘 対応表を見る</a>
    </header>

    <form method="post">
        <textarea name="code" placeholder="ここに日本語Pythonコードを書いてください">{{ code }}</textarea>
        <br><button type="submit">▶ 実行</button>
    </form>

    {% if result %}
        {% if "⚠️" in result %}
            <div class="error">{{ result }}</div>
        {% else %}
            <pre>{{ result }}</pre>
        {% endif %}
    {% endif %}
</body>
</html>
"""

# --- 対応表ページ ---
HTML_WORDS = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>対応表 - 日本語Python</title>
    <style>
        body { font-family: 'Noto Sans JP', sans-serif; background: #f9fafb; margin: 0; padding: 0; text-align: center; }
        header { background: #0078D7; color: white; padding: 15px; }
        table { width: 90%; margin: 20px auto; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
        th, td { padding: 10px; border-bottom: 1px solid #ddd; }
        th { background: #e8f3ff; }
        tr:hover { background: #f1f7ff; }
        a { color: white; text-decoration: none; }
        footer { margin: 20px; color: #777; font-size: 14px; }
    </style>
</head>
<body>
    <header>
        <h1>📘 日本語Python 対応表</h1>
        <a href="/">🏠 実行画面に戻る</a>
    </header>

    <table>
        <tr><th>Pythonコード</th><th>日本語</th><th>意味</th></tr>
        {% for jp, py in mapping.items() %}
            <tr>
                <td><code>{{ py }}</code></td>
                <td>{{ jp }}</td>
                <td>{{ descriptions.get(jp, "説明なし") }}</td>
            </tr>
        {% endfor %}
    </table>

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
    return render_template_string(HTML_MAIN, code=code, result=result, mapping=mapping)

@app.route("/words")
def words():
    return render_template_string(HTML_WORDS, mapping=mapping, descriptions=descriptions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
