from flask import Flask, request, jsonify
from models import db, ToDo, User
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/create-todo", methods=["POST"])
def create_todo():
    data = request.get_json()
    description = data.get("description")
    if not description:
        return jsonify({"error": "Task description is required"}), 400
    todo = ToDo(description=description)
    db.session.add(todo)
    db.session.commit()
    return jsonify({"message": "Task has been created", "todo": todo.to_dict()}), 201


@app.route("/get-todo", methods=["GET"])
def get_todo():
    todo_id = request.args.get("id")
    if not todo_id:
        return jsonify({"error": "Specifying of id is required"}), 400
    todo = ToDo.query.get(todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"todo": todo.to_dict()}), 200


@app.route("/get-all-todo", methods=["GET"])
def get_all_todo():
    todos = ToDo.query.all()
    todos_list = [todo.to_dict() for todo in todos]
    return jsonify({"todos": todos_list}), 200


@app.route("/update-todo", methods=["PUT", "PATCH"])
def update_todo():
    data = request.get_json()
    todo_id = data.get("id")
    new_description = data.get("description")
    if not todo_id or not new_description:
        return jsonify({"error": "You need to set id and fill in with new description"}), 400
    todo = ToDo.query.get(todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    todo.description = new_description
    db.session.commit()
    return jsonify({"message": "Task has been updated", "todo": todo.to_dict()}), 200


@app.route("/delete-todo", methods=["DELETE"])
def delete_todo():
    data = request.get_json()
    todo_id = data.get("id")
    if not todo_id:
        return jsonify({"error": "Specifying of id is required"}), 400
    todo = ToDo.query.get(todo_id)
    if not todo:
        return jsonify({"error": "Not Found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Task has been deleted"}), 200


@app.route('/delete-all-todo', methods=['DELETE'])
def delete_all_todo():
    try:
        num_deleted = db.session.query(ToDo).delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_deleted} tasks."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete tasks: {str(e)}"}), 500

@app.route("/get-users", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = [user.to_dict() for user in users]
    return jsonify({"users": users_list}), 200


@app.route("/add-user", methods=["POST"])
def add_user():
    data = request.get_json()
    telegram_id = data.get("telegram_id")
    group = data.get("group")
    if not telegram_id or not group:
        return jsonify({"error": "telegram_id and group are required"}), 400
    if User.query.filter_by(telegram_id=telegram_id).first():
        return jsonify({"error": "User already exists"}), 400
    new_user = User(telegram_id=telegram_id, group=group)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully", "user": new_user.to_dict()}), 201


@app.route("/delete-user", methods=["DELETE"])
def delete_user():
    data = request.get_json()
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        return jsonify({"error": "telegram_id is required"}), 400
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@app.route("/edit-user", methods=["PUT", "PATCH"])
def edit_user():
    data = request.get_json()
    telegram_id = data.get("telegram_id")
    new_group = data.get("group")
    if not telegram_id or not new_group:
        return jsonify({"error": "telegram_id and new group are required"}), 400
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.group = new_group
    db.session.commit()
    return jsonify({"message": "User updated successfully", "user": user.to_dict()}), 200


def check_domain(domain):
    if not domain.startswith("http"):
        domain = "https://" + domain
    try:
        response = requests.get(domain, timeout=5)
        status = response.status_code
        ssl_ok = "OK"
        availability = "available" if status == 200 else "not available"
    except requests.exceptions.SSLError:
        ssl_ok = "Failed"
        status = "N/A"
        availability = "not available"
    except Exception:
        ssl_ok = "Error"
        status = "N/A"
        availability = "not available"
    return {"domain": domain, "ssl": ssl_ok, "status": status, "availability": availability}


@app.route("/search-domains", methods=["POST"])
def search_domains():
    data = request.get_json()
    domains_input = data.get("domains")
    if not domains_input:
        return jsonify({"error": "No domains provided"}), 400
    if isinstance(domains_input, str):
        domains = [d.strip() for d in domains_input.splitlines() if d.strip()]
    elif isinstance(domains_input, list):
        domains = domains_input
    else:
        return jsonify({"error": "Invalid input format"}), 400
    results = [check_domain(d) for d in domains]
    return jsonify({"results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
