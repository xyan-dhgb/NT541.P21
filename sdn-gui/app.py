from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'dev'

# Lưu topology tạm thời (trong RAM)
topology = {
    "core": {
        "name": "Core Switch",
        "children": []
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Lấy dữ liệu từ form
        khoa = request.form.get("khoa")
        vxlan_id = request.form.get("vxlan_id")
        teacher_name = request.form.get("teacher_name")
        teacher_ip = request.form.get("teacher_ip")
        student_name = request.form.get("student_name")
        student_ip = request.form.get("student_ip")

        # Tạo dist switch mới
        dist_switch = {
            "name": f"Dist Switch - {khoa}",
            "vxlan_id": vxlan_id,
            "users": []
        }

        # Thêm giảng viên
        if teacher_name and teacher_ip:
            dist_switch["users"].append({
                "name": teacher_name,
                "ip": teacher_ip,
                "role": "teacher"
            })

        # Thêm sinh viên
        if student_name and student_ip:
            dist_switch["users"].append({
                "name": student_name,
                "ip": student_ip,
                "role": "student"
            })

        # Thêm vào cây chính
        topology["core"]["children"].append(dist_switch)

        return redirect(url_for("index"))

    return render_template("index.html", topology=topology)

if __name__ == "__main__":
    app.run(debug=True)
