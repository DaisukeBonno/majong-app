from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# DB初期化
def init_db():
    conn = sqlite3.connect("mahjong.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        p1 INTEGER, p2 INTEGER, p3 INTEGER, p4 INTEGER,
        r1 REAL, r2 REAL, r3 REAL, r4 REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()


def calculate_score(scores, uma=(30, 10, -10, -30)):
    players = list(enumerate(scores))
    players.sort(key=lambda x: x[1], reverse=True)

    results = [0]*4

    # 同点処理
    groups = []
    current = [players[0]]

    for i in range(1,4):
        if players[i][1] == players[i-1][1]:
            current.append(players[i])
        else:
            groups.append(current)
            current = [players[i]]
    groups.append(current)

    rank_index = 0
    for group in groups:
        size = len(group)
        uma_slice = uma[rank_index:rank_index+size]
        avg_uma = sum(uma_slice)/size

        for idx, score in group:
            diff = (score - 30000)//1000
            results[idx] = diff + avg_uma

        rank_index += size

    return results


@app.route("/", methods=["GET","POST"])
def index():
    names = ["P1","P2","P3","P4"]
    scores = ["","","",""]
    results = None

    conn = sqlite3.connect("mahjong.db")
    c = conn.cursor()

    if request.method == "POST":
        names = request.form.getlist("name")
        scores = request.form.getlist("score")

        try:
            scores_int = []
            for s in scores:
                if s == "":
                    scores_int.append(25000)
                else:
                    s = s.translate(str.maketrans("０１２３４５６７８９","0123456789"))
                    scores_int.append(int(s)*100)

            results = calculate_score(scores_int)

            # DB保存
            c.execute("""
            INSERT INTO history (p1,p2,p3,p4,r1,r2,r3,r4)
            VALUES (?,?,?,?,?,?,?,?)
            """, (*scores_int, *results))
            conn.commit()

        except:
            results = ["エラー"]*4

    # 履歴取得
    c.execute("SELECT * FROM history ORDER BY id DESC")
    rows = c.fetchall()

    # 累計・順位計算
    totals = [0]*4
    ranks = [[0]*4 for _ in range(4)]

    for row in rows:
        scores_db = row[1:5]
        results_db = row[5:9]

        for i in range(4):
            totals[i] += results_db[i]

        ranked = sorted(enumerate(scores_db), key=lambda x:x[1], reverse=True)
        for rank,(idx,_) in enumerate(ranked):
            ranks[idx][rank]+=1

    conn.close()

    return render_template("index.html",
                           names=names,
                           scores=scores,
                           results=results,
                           history=rows,
                           totals=totals,
                           ranks=ranks)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")