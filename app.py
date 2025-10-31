from flask import Flask, request, render_template_string, session
import io
import sys

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

# 説明文（例付き）
EXAMPLES = {
    "表示": "例: 表示('こんにちは') → 画面に文字を出す",
    "もし": "例: もし x > 5: 表示('大きい')",
    "繰り返す": "例: 繰り返す i 範囲(5): 表示(i)",
    "入力": "例: 名前 = 入力('あなたの名前は？')",
    "関数": "例: 関数 あいさつ(): 表示('こんにちは')",
}

# 日本語→Pythonコード変換
def translate(jp_code: str) -> str:
    for jp in sorted(JP_TO_PY.keys(), key=len, reverse=True):
        jp_code = jp_code.replace(jp, JP_TO_PY[jp])
    return jp_code


def run_japanese_code(jp_code: str) -> str:
    py_code = translate(jp_code)
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        exec(py_code, {})
    except Exception as e:
        return f"⚠️ エラー: {e}"
    finally:
        sys.stdout = sys_stdout
    return buffer.getvalue()


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
    return render_template_string(HTML_TABLE, rows=table_rows, examples=EXAMPLES)


# 実行ページHTML
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日本語Python 実行ページ</title>
<style>
body {{ font-family: "Segoe UI", sans-serif; margin: 20px; background: #f7f7f7; }}
textarea {{ width: 100%; height: 220px; border-radius: 8px; padding: 10px; font-size: 16px; }}
button {{ margin-top: 10px; width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 8px; }}
a {{ text-decoration: none; color: #007bff; }}
pre {{ background: #222; color: #0f0; padding: 10px; border-radius: 8px; }}
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
body {{ font-family: "Segoe UI", sans-serif; margin: 20px; background: #fafafa; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
th {{ background: #f0f0f0; }}
input {{ width: 100%; padding: 8px; margin-bottom: 10px; }}
button {{ border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; }}
.copy-btn {{ background: #4CAF50; color: white; }}
.example-btn {{ background: #007bff; color: white; }}
#exampleBox {{ display: none; background: #eef; padding: 10px; margin-top: 15px; border-radius: 8px; }}
</style>
<script>
function copyText(text) {{
  navigator.clipboard.writeText(text);
  alert('「' + text + '」をコピーしました！');
}}
function showExample(key) {{
  const examples = {{ {', '.join([f"'{k}': '{v}'" for k, v in EXAMPLES.items()])} }};
  const box = document.getElementById('exampleBox');
  box.style.display = 'block';
  box.innerHTML = examples[key] || 'この語の例はまだ登録されていません。';
}}
function filterTable() {{
  let input = document.getElementById("search").value.toLowerCase();
  let rows = document.querySelectorAll("table tr");
  for (let i = 1; i < rows.length; i++) {{
    let text = rows[i].innerText.toLowerCase();
    rows[i].style.display = text.includes(input) ? "" : "none";
  }}
}}
</script>
</head>
<body>
<h1>📘 日本語→Python 対応表</h1>
<p><a href="/">← 実行画面に戻る</a></p>
<input type="text" id="search" onkeyup="filterTable()" placeholder="検索 (例: 表示)">
<table>
<tr><th>日本語</th><th>Python</th><th>操作</th></tr>
{{ rows }}
</table>
<div id="exampleBox"></div>
</body>
</html>
"""

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


