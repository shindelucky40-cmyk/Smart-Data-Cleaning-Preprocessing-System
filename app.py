"""
Smart Data Cleaning & Preprocessing System — Flask App
-------------------------------------------------------
Serves frontend and exposes REST API for upload / clean / download.
"""

import json
import os
import uuid
import numpy as np
from flask import Flask, request, jsonify, send_file, send_from_directory
from data_processor import (
    read_file,
    analyse_dataframe,
    clean_dataframe,
    preprocess_dataframe,
    df_preview,
    df_to_download_bytes,
    get_visualization_data,
)
import pandas as pd


class NumpyJSONEncoder(json.JSONEncoder):
    """Handles numpy types that the default encoder chokes on."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            if np.isnan(obj):
                return None
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)


app = Flask(__name__, static_folder="static", static_url_path="")
app.json_encoder = NumpyJSONEncoder  # type: ignore[attr-defined]
app.config["JSON_SORT_KEYS"] = False

# In-memory session store  { session_id: { "raw": df, "cleaned": df | None } }
SESSIONS: dict[str, dict] = {}

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- Page ----------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ---------- Upload ----------
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = read_file(f, f.filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"raw": df, "cleaned": None, "filename": f.filename}

    analysis = analyse_dataframe(df)
    preview = df_preview(df)

    return jsonify({
        "session_id": session_id,
        "filename": f.filename,
        "preview": preview,
        "analysis": analysis,
    })


# ---------- Clean & Preprocess ----------
@app.route("/api/clean", methods=["POST"])
def clean():
    body = request.get_json(force=True)
    session_id = body.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "Invalid session"}), 400

    df = SESSIONS[session_id]["raw"].copy()

    # --- Cleaning options ---
    clean_opts = {
        "missing_strategy": body.get("missing_strategy"),       # mean|median|mode|drop
        "remove_duplicates": body.get("remove_duplicates", False),
        "remove_constant_cols": body.get("remove_constant_cols", False),
        "trim_whitespace": body.get("trim_whitespace", False),
        "handle_outliers": body.get("handle_outliers"),         # cap|remove|null
    }

    # --- Preprocessing options ---
    preprocess_opts = {
        "encode_categorical": body.get("encode_categorical"),   # label|onehot|null
        "scale_numeric": body.get("scale_numeric"),             # standard|minmax|null
        "extract_datetime": body.get("extract_datetime", False),
        "log_transform": body.get("log_transform", False),
        "text_cleaning": body.get("text_cleaning", False),
    }

    all_changes: list[dict] = []

    # Step 1 – clean
    df, clean_changes = clean_dataframe(df, clean_opts)
    all_changes.extend(clean_changes)

    # Step 2 – preprocess
    df, preprocess_changes = preprocess_dataframe(df, preprocess_opts)
    all_changes.extend(preprocess_changes)

    SESSIONS[session_id]["cleaned"] = df

    return jsonify({
        "preview": df_preview(df),
        "changes": all_changes,
        "rows": len(df),
        "columns": len(df.columns),
    })


# ---------- Download ----------
@app.route("/api/download", methods=["GET"])
def download():
    session_id = request.args.get("session_id")
    fmt = request.args.get("format", "csv")
    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "Invalid session"}), 400

    df = SESSIONS[session_id].get("cleaned")
    if df is None:
        return jsonify({"error": "No cleaned data available. Run cleaning first."}), 400

    buf = df_to_download_bytes(df, fmt)
    ext = fmt if fmt != "xlsx" else "xlsx"
    original = SESSIONS[session_id].get("filename", "data")
    base = original.rsplit(".", 1)[0]

    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{base}_cleaned.{ext}",
        mimetype="application/octet-stream",
    )

# ---------- Visualization ----------
@app.route("/api/visualize", methods=["GET"])
def visualize():
    session_id = request.args.get("session_id")
    dtype = request.args.get("type", "raw") # "raw" or "cleaned"
    
    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "Invalid session"}), 400

    df = SESSIONS[session_id].get(dtype)
    if df is None:
        return jsonify({"error": f"No {dtype} data available."}), 400

    vis_data = get_visualization_data(df)
    return jsonify(vis_data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
