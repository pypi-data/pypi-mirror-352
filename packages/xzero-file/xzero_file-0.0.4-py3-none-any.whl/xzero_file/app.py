import os
import argparse
from flask import (
    Flask, send_file, send_from_directory, Blueprint,
    jsonify, request, redirect, url_for
)
from werkzeug.utils import secure_filename
from .service import is_safe_path, get_public_ip, display_qr_code_in_terminal

WORKDIR = "."

app = Flask("x-file")

api_bp = Blueprint("api", __name__, url_prefix="/api")

app.config["STATIC_DIR"] = os.path.join(os.path.dirname(__file__), "assets")


@app.route("/assets/<path:name>")
def get_static_file(name):
    return send_from_directory(app.config["STATIC_DIR"], name, as_attachment=True)


@app.route("/")
def get_home():
    return send_file(os.path.join(app.config["STATIC_DIR"], "index.html"))


@api_bp.route("/files")
def list_file():
    name = request.args.get('name', '')
    req_path = os.path.join(WORKDIR, name)
    if not is_safe_path(WORKDIR, req_path):
        req_path = WORKDIR
    file_list = []
    parent_path = os.path.join(req_path, "..")
    if is_safe_path(WORKDIR, parent_path):
        file_list.append({"name": "..", "is_dir": True})
    for f in os.listdir(req_path):
        file_list.append({"name": f, "is_dir": os.path.isdir(os.path.join(req_path, f))})
    return jsonify({"files": file_list})

@api_bp.route("files", methods=["PUT"])
def upload_file():
    # if not request.headers.get("Transfer-Encoding") == "chunked":
    #     return jsonify({"error": "Request must use chunked transfer encoding"}), 400
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "need filename"}), 400

    f_path = os.path.abspath(os.path.join(WORKDIR, filename))
    if not is_safe_path(WORKDIR, f_path):
        return jsonify({"error": "not allowed filename"}), 400
    # f_path = secure_filename(f_path)
        
    with open(f_path, "wb") as f:
        while True:
            chunk = request.stream.read(8192)
            if not chunk:
                break
            f.write(chunk)
    return jsonify({"file": os.path.relpath(f_path, WORKDIR)})
        

@api_bp.route('download')
def download_file():
    name = request.args.get('name', '')
    req_path = os.path.join(WORKDIR, name)
    if not is_safe_path(WORKDIR, req_path):
        req_path = WORKDIR
    
    if os.path.exists(req_path) and os.path.isfile(req_path):
        return send_file(req_path, as_attachment=True)
    return "File not found", 404
    

app.register_blueprint(api_bp)


def main(args):
    global WORKDIR
    WORKDIR = os.path.abspath(args.cwd)
    print(f" * workdir: {WORKDIR}")
    print(f" * static dir: {app.config['STATIC_DIR']}")
    if args.host == '0.0.0.0':
        ip = get_public_ip()
        url = f'http://{ip}:{args.port}'
        print("** visit: ", url)
        display_qr_code_in_terminal(url)

    app.run(debug=False, host=args.host, port=args.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="xzero_file upload and download file")

    # Add arguments
    parser.add_argument("--host", default="0.0.0.0", help="host default 0.0.0.0")
    parser.add_argument("--port", type=int, default=8000, help="port default 8000")
    parser.add_argument("--cwd", default=".", help="work dir")

    # Parse the arguments
    args = parser.parse_args()
    main(args)
