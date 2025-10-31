from flask import Flask, request, render_template_string, session
import io
import sys
import contextlib

app = Flask(__name__)
app.secret_key = "nihongo-python-secret"

# 日本語→Python変換マップ（最新版）
JP_TO_PY = {
    "表示": "print",
    "もし": "if",
    "でなければ": "else",
    "繰り返す": "for",
    "範囲": "range",
    "入力": "input",
    "を足す": "+=",
    "を引く": "-=",
    "を掛ける": "*=",
    "を割る": "/=",
    "等しい": "==",
    "以上": ">=",
    "以下": "<=",
    "大きい": ">",
    "小さい": "<",
    "かつ": "and",
    "または": "or",
    "真": "True",
    "偽": "False",
    "終了": "break",
    "続ける": "continue",
    "関数": "def",
    "戻す": "return",
    "リスト": "list",
    "追加": "append",
    "削除": "remove",
    "長さ": "len",
    "インポート": "import",
    "時間": "time",
    "待つ": "sleep",
    "ランダム": "random",
    "から選ぶ": "choice",
    "辞書": "dict",
    "キー": "keys",
    "値": "values",
}

    py_code = jp_code
    for jp, py in replacements.items():
        py_code = py_code.replace(jp, py)
    return py_code

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

# 説明文（例付き）
EXAMPLES = {
    "表示": "例: 表示('こんにちは') → 画面に文字を出す",
    "もし": "例: もし x > 5: 表示('大きい')",
    "繰り返す": "例: 繰り返す i 範囲(5): 表示(i)",
    "入力": "例: 名前 = 入力('あなたの名前は？')",
    "関数": "例: 関数 あいさつ(): 表示('こんにちは')",
}

# --- 日本語 → Python 変換関数 ---
def translate(jp_code: str) -> str:
    """日本語コードをPythonコードに変換"""
    py_code = jp_code
    for jp, py in JP_TO_PY.items():
        py_code = py_code.replace(jp, py)
    return py_code

# --- 日本語コード実行 + エラー翻訳 ---
def run_japanese_code(jp_code):
    try:
        py_code = translate(jp_code)
        # 出力を取得
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(py_code, {})
        return output.getvalue()
    except Exception as e:
        # エラーを日本語に変換
        error_message = translate_error_to_japanese(str(e))
        return f"エラー: {error_message}"
def translate_error_to_japanese(error_text: str) -> str:
    """英語のエラーメッセージを日本語に変換"""
    replacements = {
        "NameError": "名前が定義されていません",
        "SyntaxError": "文法エラーです",
        "TypeError": "型の使い方が正しくありません",
        "ValueError": "値が不正です",
        "IndexError": "インデックスの範囲外です",
        "KeyError": "指定されたキーが見つかりません",
        "ZeroDivisionError": "0で割ることはできません",
        "FileNotFoundError": "ファイルが見つかりません",
        "ImportError": "モジュールの読み込みに失敗しました",
        "AttributeError": "指定された属性が存在しません",
    }

    for en, jp in replacements.items():
        if en in error_text:
            return jp + "（" + error_text + "）"
    return "不明なエラーです: " + error_text

# 実行ページ
@app.route("/", methods=["GET", "POST"])
def index():
    code = session.get("saved_code", "")
    result = ""
    if request.method == "POST":
        code = request.form["code"]
        session["saved_code"] = code
        result = run_japanese_code(code)
    return render_template_string(HTML_MAIN, code=code, result=result)


# 対応表ページ
@app.route("/table")
def table():
    table_rows = "".join(
        f"""
        <tr>
            <td>{jp}</td>
            <td>{py}</td>
            <td>
                <button onclick="copyText('{jp}')">📋 コピー</button>
                <button onclick="showExample('{jp}')">💡 例を見る</button>
            </td>
        </tr>
        """
        for jp, py in JP_TO_PY.items()
    )
    return render_template_string(HTML_TABLE, rows=table_rows, examples=EXAMPLES, escape=False)


# 実行ページHTML
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日本語Python 実行ページ</title>
<style>
body { font-family: "Segoe UI", sans-serif; margin: 20px; background: #f7f7f7; }
textarea { width: 100%; height: 220px; border-radius: 8px; padding: 10px; font-size: 16px; }
button { margin-top: 10px; width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 8px; }
a { text-decoration: none; color: #007bff; }
pre { background: #222; color: #0f0; padding: 10px; border-radius: 8px; }
</style>
</head>
<body>
<h1>🐍 日本語Python 実行ページ</h1>
<p><a href="/table">👉 対応表を見る</a></p>
<form method="post">
<textarea name="code">{{ code or '' }}</textarea>
<button type="submit">▶ 実行</button>
</form>
<h3>結果</h3>
<pre>{{ result }}</pre>
</body>
</html>
"""

# 対応表ページHTML
HTML_TABLE = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>対応表</title>
<style>
body { font-family: "Segoe UI", sans-serif; margin: 20px; background: #fafafa; }
h1 { text-align: center; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; border-radius: 8px; overflow: hidden; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
th { background: #f0f0f0; font-weight: bold; }
input[type="text"] {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
}
button {
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  margin: 2px;
}
.copy-btn { background: #4CAF50; color: white; }
.example-btn { background: #007bff; color: white; }
#exampleBox {
  display: none;
  background: #eef;
  padding: 15px;
  margin-top: 20px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  font-size: 16px;
}
a { text-decoration: none; color: #007bff; }
@media (max-width: 600px) {
  th, td { font-size: 14px; padding: 6px; }
  button { padding: 5px 8px; font-size: 12px; }
}
</style>
<script>
function copyText(text) {
  navigator.clipboard.writeText(text);
  alert('「' + text + '」をコピーしました！');
}
function showExample(key) {
  const examples = {{ examples | tojson }};
  const box = document.getElementById('exampleBox');
  box.style.display = 'block';
  box.innerHTML = '<b>' + key + '</b><br>' + (examples[key] || 'この語の例はまだ登録されていません。');
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}
function filterTable() {
  let input = document.getElementById("search").value.toLowerCase();
  let rows = document.querySelectorAll("table tr");
  for (let i = 1; i < rows.length; i++) {
    let text = rows[i].innerText.toLowerCase();
    rows[i].style.display = text.includes(input) ? "" : "none";
  }
}
</script>
</head>
<body>
<h1>📘 日本語 → Python 対応表</h1>
<p style="text-align:center;"><a href="/">← 実行画面に戻る</a></p>
<input type="text" id="search" onkeyup="filterTable()" placeholder="🔍 検索 (例: 表示)">
<table>
<tr><th>日本語</th><th>Python</th><th>操作</th></tr>
{{ rows | safe }}
</table>
<div id="exampleBox"></div>
</body>
</html>
"""

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)













