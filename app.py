import os
import sys
import json

# Đảm bảo hiển thị Unicode tiếng Việt trên Terminal Windows không bị lỗi
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datetime import datetime
from collections import Counter
from flask import Flask, render_template, jsonify, request, send_from_directory, abort

from src.config import BASE_DIR, ASSETS_DIR, DATA_DIR, CASES_FILE, WORD_LENGTH, MAX_ATTEMPTS
from src.data_manager import DataManager

app = Flask(__name__, static_folder="static", template_folder="templates")
data_manager = DataManager()
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")

# Route phục vụ tài nguyên ảnh & âm thanh dùng chung
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    for candidate_dir in [ASSETS_DIR, os.path.join(BASE_DIR, "assests")]:
        full_path = os.path.join(candidate_dir, filename)
        if os.path.exists(full_path):
            return send_from_directory(candidate_dir, filename)
    abort(404)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/cases", methods=["GET"])
def get_cases():
    """Trả về danh sách vụ án (ẩn từ bí mật để chống soi F12)."""
    data_manager.load_cases()
    cases = []
    for c in data_manager.cases:
        cases.append({
            "id": c.get("id"),
            "case_name": c.get("case_name"),
            "image": c.get("image"),
            "reveal_image": c.get("reveal_image") or c.get("correct_image") or c.get("solved_image"),
            "clues_count": len(c.get("clues", [])),
            "word_length": len(c.get("word", "ABCDE"))
        })
    return jsonify(cases)

@app.route("/api/clue/<int:case_id>/<int:clue_idx>", methods=["GET"])
def get_clue(case_id, clue_idx):
    """Lấy nội dung manh mối theo thứ tự (bắt đầu từ 0)."""
    data_manager.load_cases()
    for c in data_manager.cases:
        if c.get("id") == case_id:
            clues = c.get("clues", [])
            if 0 <= clue_idx < len(clues):
                return jsonify({"success": True, "clue": clues[clue_idx]})
            return jsonify({"success": False, "error": "Đã hết manh mối!"})
    return jsonify({"success": False, "error": "Không tìm thấy vụ án!"}), 404

@app.route("/api/check", methods=["POST"])
def check_guess():
    """Kiểm tra từ đoán và trả về màu sắc chuẩn Wordle 2 lượt."""
    data = request.get_json() or {}
    case_id = data.get("case_id")
    guess = data.get("guess", "").strip().upper()
    attempt = data.get("attempt", 1) # Lượt đoán thứ mấy (1-6)

    # Đọc lại dữ liệu mới nhất
    data_manager.load_cases()
    target_case = None
    for c in data_manager.cases:
        if c.get("id") == case_id:
            target_case = c
            break

    if not target_case:
        return jsonify({"success": False, "error": "Vụ án không tồn tại"}), 404

    target_word = target_case.get("word", "").strip().upper()
    if len(guess) != len(target_word):
        return jsonify({"success": False, "error": f"Từ phải gồm {len(target_word)} chữ cái"}), 400

    # Thuật toán so khớp 2 lượt chuẩn xác
    target_counts = Counter(target_word)
    result_status = ["absent"] * len(target_word)

    # Lượt 1: Đúng chữ, đúng vị trí (green)
    for i in range(len(target_word)):
        if guess[i] == target_word[i]:
            result_status[i] = "correct"
            target_counts[guess[i]] -= 1

    # Lượt 2: Có chữ nhưng sai vị trí (yellow)
    for i in range(len(target_word)):
        if result_status[i] != "correct":
            char = guess[i]
            if target_counts.get(char, 0) > 0:
                result_status[i] = "present"
                target_counts[char] -= 1
            else:
                result_status[i] = "absent"

    is_correct = (guess == target_word)
    reveal_word = target_word if (is_correct or attempt >= MAX_ATTEMPTS) else None
    
    # Lấy đường dẫn ảnh mở khóa khi trả lời đúng
    reveal_img = None
    if is_correct:
        reveal_img = target_case.get("reveal_image") or target_case.get("correct_image") or target_case.get("solved_image")

    return jsonify({
        "success": True,
        "result_status": result_status,
        "is_correct": is_correct,
        "is_game_over": is_correct or (attempt >= MAX_ATTEMPTS),
        "target_word": reveal_word,
        "reveal_image": reveal_img
    })

@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """Trả về bảng xếp hạng đã sắp xếp theo chuẩn thi đấu Competitive Programming."""
    standings = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                standings = json.load(f)
        except Exception as e:
            print(f"Lỗi đọc leaderboard: {e}")

    # Sắp xếp:
    # 1. Số câu giải được (solved) GIẢM DẦN
    # 2. Tổng điểm (score) GIẢM DẦN
    # 3. Tổng thời gian (total_time) TĂNG DẦN
    standings.sort(key=lambda x: (-x.get("solved", 0), -x.get("score", 0), x.get("total_time", 999999)))

    # Gắn Rank (1, 2, 3...)
    for rank, entry in enumerate(standings, start=1):
        entry["rank"] = rank

    return jsonify(standings)

@app.route("/api/submit_contest", methods=["POST"])
def submit_contest():
    """Nộp kết quả thi đấu chuyên án và cập nhật bảng xếp hạng."""
    submission = request.get_json() or {}
    handle = submission.get("handle", "Anonymous_Detective").strip()
    if not handle:
        handle = "Anonymous_Detective"

    score = submission.get("score", 0)
    solved = submission.get("solved", 0)
    total_time = submission.get("total_time", 0)
    cases_detail = submission.get("cases_detail", {})

    record = {
        "handle": handle,
        "score": score,
        "solved": solved,
        "total_time": total_time,
        "cases_detail": cases_detail,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    standings = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                standings = json.load(f)
        except Exception:
            standings = []

    standings.append(record)

    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(standings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi ghi leaderboard: {e}")

    # Tính thứ hạng của thí sinh vừa nộp
    standings.sort(key=lambda x: (-x.get("solved", 0), -x.get("score", 0), x.get("total_time", 999999)))
    rank = 1
    for idx, item in enumerate(standings, start=1):
        if item.get("handle") == handle and item.get("score") == score and item.get("total_time") == total_time:
            rank = idx
            break

    return jsonify({"success": True, "rank": rank, "total_contestants": len(standings)})

if __name__ == "__main__":
    print("\n" + "="*50)
    print("[CHUYEN AN] MAY CHU THI DAU DANG KHOI CHAY...")
    print("Truy cap Web tai dia chi: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
