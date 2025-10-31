from flask import Flask, request, render_template_string, session
import io
import contextlib

app = Flask(__name__)
app.secret_key = "nihongo-python-secret"

# -------------------------------
# 🔤 日本語 → Python 変換マップ
# -------------------------------
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

# -------------------------------
# 🈁 日本語 → Python コード変換
# -------------------------------
def translate(jp_code: str) -> str:
    """日本語コードをPythonコードに変換"""
    py_code = jp_code
    for jp, py in JP_TO_PY.items():
        py_code = py_code.replace(jp, py)
    return py_code


# -------------------------------
# ⚠ やさしい日本語エラーメッセージ
# -------------------------------
ERROR_MESSAGES = {
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

def translate_error_to_japanese(e: Exception) -> str:
    """英語のエラーメッセージを日本語に変換"""
    error_type = type(e).__name__
    if error_type in ERROR_MESSAGES:
        return f"{ERROR_MESSAGES[error_type]}\n\n（詳細: {str(e)}）"
    else:
        return f"不明なエラーが発生しました: {error_type}\n{str(e)}"


# -------------------------------
# 💡 日本語Python 実行関数
# -------------------------------
def run_japanese_code(jp_code):
    try:
        py_code = translate(jp_code)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(py_code, {})
        return output.getvalue()
    except Exception as e:
        return f"⚠ エラー:\n{translate_error_to_japanese(e)}"


# -------------------------------
# 🌐 Flaskルート設定
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    code = session.get("saved_code", "")
    result = ""
    if request.method == "POST":
        code = request.form["code"]
        session["saved_code"] = code
        result = run_japanese_code(code)
    return render_template_string(HTML_MAIN, code=code, result=result)


@app.route("/table")
def table():
    table_rows = "".join(
        f"""
        <tr>
            <td>{jp}</td>
            <td>{py}</td>
            <td><button onclick="copyText('{jp}')">📋 コピー</button></td>
        </tr>
        """
        for jp, py in JP_TO_PY.items()
    )
    return render_template_string(HTML_TABLE, rows=table_rows)


# -------------------------------
# 🖋 HTMLテンプレート
# -------------------------------
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>日本語Python 実行ページ</title>
<style>
  body {
    font-family: 'Arial', sans-serif;
    background-color: #f0f0f0;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
  }

  .container {
    width: 90%;
    max-width: 400px;
    background-color: #fff;
    margin-top: 30px;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  h1 {
    text-align: center;
    font-size: 20px;
    color: #333;
  }

  textarea {
    width: 100%;
    height: 200px;
    padding: 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 8px;
    resize: vertical;
    box-sizing: border-box;
  }

  button {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    margin-top: 10px;
  }

  button:hover {
    background-color: #0056b3;
  }

  .result-box {
    margin-top: 15px;
    padding: 10px;
    background-color: #fafafa;
    border-radius: 8px;
    font-size: 14px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  }
</style>
</head>
<body>
  <div class="container">
    <h1>📘 日本語 → Python 対応表</h1>
    <p><a href="/">← 実行画面に戻る</a></p>
    <input type="text" id="search" onkeyup="filterTable()" placeholder="🔍 検索 (例: 表示)">
    <table>
      <tr><th>日本語</th><th>Python</th><th>操作</th></tr>
      {{ rows | safe }}
    </table>
    <div id="exampleBox"></div>
  </div>
</body>
</html>
"""

HTML_TABLE = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>対応表</title>
<style>
  /* 対応表ページの基本スタイル */
body {
  font-family: "Noto Sans JP", sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f5f6fa;
  color: #333;
  text-align: center;
}

h1 {
  background-color: #4CAF50;
  color: white;
  padding: 12px;
  margin: 0;
  font-size: 20px;
}

/* テーブル全体のデザイン */
table {
  width: 95%;
  margin: 15px auto;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 10px;
  overflow: hidden;
}

th, td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-size: 14px;
}

th {
  background-color: #4CAF50;
  color: white;
  font-size: 15px;
}

/* 行を交互に少し色分け */
tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* スマホ対応 */
@media (max-width: 768px) {
  table {
    width: 100%;
    font-size: 13px;
  }

  th, td {
    display: block;
    width: 100%;
    box-sizing: border-box;
    text-align: left;
    padding: 8px;
  }

  tr {
    margin-bottom: 10px;
    display: block;
    border: 1px solid #ddd;
    border-radius: 10px;
  }

  th {
    background-color: #4CAF50;
    color: white;
    font-size: 14px;
    border-bottom: none;
  }

  td::before {
    content: attr(data-label);
    font-weight: bold;
    display: block;
    margin-bottom: 4px;
    color: #666;
  }
}
</style>

<script>
function copyText(text) {
  navigator.clipboard.writeText(text);
  alert('「' + text + '」をコピーしました！');
}
</script>
</head>
<body>
<h1>📘 日本語 → Python 対応表</h1>
<p><a href="/">← 実行画面に戻る</a></p>
<table>
<tr><th>日本語</th><th>Python</th><th>操作</th></tr>
{{ rows | safe }}
</table>
</body>
</html>
"""

# -------------------------------
# 🚀 サーバ起動
# -------------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




