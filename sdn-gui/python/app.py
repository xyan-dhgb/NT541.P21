from flask import Flask, render_template, request, redirect, url_for, flash

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
        khoa = request.form.get("khoa").strip()
        vxlan_id = request.form.get("vxlan_id").strip()
        teacher_name = request.form.get("teacher_name").strip()
        teacher_ip = request.form.get("teacher_ip").strip()
        student_name = request.form.get("student_name").strip()
        student_ip = request.form.get("student_ip").strip()

        # Kiểm tra nếu bất kỳ trường nào bị bỏ trống
        if not khoa or not vxlan_id or not teacher_name or not teacher_ip or not student_name or not student_ip:
            flash("Vui lòng điền đầy đủ tất cả các trường thông tin!", "error")
            return render_template(
                "index.html",
                topology=topology,
                form_data={
                    "khoa": khoa,
                    "vxlan_id": vxlan_id,
                    "teacher_name": teacher_name,
                    "teacher_ip": teacher_ip,
                    "student_name": student_name,
                    "student_ip": student_ip,
                },
            )

        # Kiểm tra nếu khoa đã tồn tại
        for dist in topology["core"]["children"]:
            if dist["name"].lower() == f"Dist Switch - {khoa}".lower():
                # Kiểm tra trùng thông tin giảng viên
                for user in dist["users"]:
                    if user["name"].lower() == teacher_name.lower() and user["ip"] == teacher_ip and user["role"] == "teacher":
                        flash(f"Giảng viên '{teacher_name}' với IP '{teacher_ip}' đã tồn tại trong khoa '{khoa}'!", "error")
                        return render_template(
                            "index.html",
                            topology=topology,
                            form_data={
                                "khoa": khoa,
                                "vxlan_id": vxlan_id,
                                "teacher_name": teacher_name,
                                "teacher_ip": teacher_ip,
                                "student_name": student_name,
                                "student_ip": student_ip,
                            },
                        )

                # Kiểm tra trùng thông tin sinh viên
                for user in dist["users"]:
                    if user["name"].lower() == student_name.lower() and user["ip"] == student_ip and user["role"] == "student":
                        flash(f"Sinh viên '{student_name}' với IP '{student_ip}' đã tồn tại trong khoa '{khoa}'!", "error")
                        return render_template(
                            "index.html",
                            topology=topology,
                            form_data={
                                "khoa": khoa,
                                "vxlan_id": vxlan_id,
                                "teacher_name": teacher_name,
                                "teacher_ip": teacher_ip,
                                "student_name": student_name,
                                "student_ip": student_ip,
                            },
                        )

                # Nếu không trùng thông tin, thêm vào khoa đã tồn tại
                dist["users"].append({
                    "name": teacher_name,
                    "ip": teacher_ip,
                    "role": "teacher"
                })
                dist["users"].append({
                    "name": student_name,
                    "ip": student_ip,
                    "role": "student"
                })
                flash(f"Thông tin đã được thêm vào khoa '{khoa}'!", "success")
                return redirect(url_for("index"))

        # Nếu khoa chưa tồn tại, tạo dist switch mới
        dist_switch = {
            "name": f"Dist Switch - {khoa}",
            "vxlan_id": vxlan_id,
            "users": []
        }

        # Thêm giảng viên
        dist_switch["users"].append({
            "name": teacher_name,
            "ip": teacher_ip,
            "role": "teacher"
        })

        # Thêm sinh viên
        dist_switch["users"].append({
            "name": student_name,
            "ip": student_ip,
            "role": "student"
        })

        # Thêm vào cây chính
        topology["core"]["children"].append(dist_switch)
        flash(f"Khoa '{khoa}' đã được thêm thành công!", "success")

        # Redirect đến trang GET để tránh gửi lại dữ liệu POST
        return redirect(url_for("index"))

    # Xử lý GET: hiển thị giao diện với dữ liệu hiện tại
    return render_template("index.html", topology=topology, form_data={})

if __name__ == "__main__":
    app.run(debug=True)