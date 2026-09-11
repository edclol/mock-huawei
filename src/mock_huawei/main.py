"""
HMS Core API Mock Server
模拟华为 HMS Core 相关接口，用于本地开发与测试
"""

from flask import Flask, request, jsonify
import time
import uuid
import random
import logging
import time
import uuid
from flask import g
import logging
import time
import uuid
from flask import g


import base64
app = Flask(__name__)




# ========== 日志配置 ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("healthkit_mock")


@app.before_request
def log_request():
    """请求进入时记录完整入参"""
    g.request_id = str(uuid.uuid4())[:8]
    g.start_time = time.time()

    # 1. 记录请求方法与路径
    logger.info("[%s] >>> %s %s", g.request_id, request.method, request.path)

    # 2. 记录完整请求头
    headers_dict = dict(request.headers)
    logger.info("[%s] Request Headers: %s", g.request_id, headers_dict)

    # 3. 记录完整查询参数 (GET)
    if request.args:
        logger.info("[%s] Query Params: %s", g.request_id, dict(request.args))

    # 4. 记录完整请求体 (POST/PUT/PATCH)
    if request.method in ("POST", "PUT", "PATCH"):
        body = request.get_data(as_text=True)
        logger.info("[%s] Request Body: %s", g.request_id, body)


@app.after_request
def log_response(response):
    """请求返回时记录完整出参"""
    duration_ms = round((time.time() - getattr(g, "start_time", time.time())) * 1000, 2)
    request_id = getattr(g, "request_id", "unknown")

    # 1. 记录响应状态与耗时
    logger.info("[%s] <<< Status: %s | Duration: %sms", request_id, response.status_code, duration_ms)

    # 2. 记录完整响应头
    headers_dict = dict(response.headers)
    logger.info("[%s] Response Headers: %s", request_id, headers_dict)

    # 3. 记录完整响应体
    body = response.get_data(as_text=True)
    logger.info("[%s] Response Body: %s", request_id, body)

    return response

# ==================== 工具函数 ====================

def success_response(data=None, message="Success"):
    """统一成功响应格式"""
    return jsonify({
        "subCode": "0",
        "subMsg": message,
        "data": data or {}
    }), 200


def error_response(sub_code, sub_msg, http_status=400):
    """统一错误响应格式"""
    return jsonify({
        "subCode": str(sub_code),
        "subMsg": sub_msg
    }), http_status


# ==================== 1. Auth Example ====================
# 参考: https://developer.huawei.com/consumer/cn/doc/HMSCore-Guides/auth-example-0000001054581058

@app.route("/oauth2/v3/token", methods=["POST"])
def oauth_token():
    """
    模拟 OAuth2 Token 端点
    支持 authorization_code 和 refresh_token 两种 grant_type
    """
    grant_type = request.form.get("grant_type") or request.json.get("grant_type") if request.is_json else request.form.get("grant_type")
    client_id = request.form.get("client_id") or (request.json.get("client_id") if request.is_json else None)

    if not grant_type:
        return error_response(12002, "missing required parameter: grant_type")

    if grant_type == "authorization_code":
        code = request.form.get("code") or (request.json.get("code") if request.is_json else None)
        if not code:
            return error_response(12002, "missing required parameter: code")
        # 模拟返回 token
        return jsonify({
            "access_token": f"mock_access_token_{uuid.uuid4().hex[:16]}",
            "expires_in": 3600,
            "refresh_token": f"mock_refresh_token_{uuid.uuid4().hex[:16]}",
            "scope": "openid profile email",
            "token_type": "Bearer"
        }), 200

    elif grant_type == "refresh_token":
        refresh_token = request.form.get("refresh_token") or (request.json.get("refresh_token") if request.is_json else None)
        if not refresh_token:
            return error_response(12002, "missing required parameter: refresh_token")
        return jsonify({
            "access_token": f"mock_access_token_{uuid.uuid4().hex[:16]}",
            "expires_in": 3600,
            "refresh_token": f"mock_refresh_token_{uuid.uuid4().hex[:16]}",
            "scope": "openid profile email",
            "token_type": "Bearer"
        }), 200

    else:
        return error_response(12003, f"unsupported grant_type: {grant_type}")


@app.route("/userinfo/v2/me", methods=["GET"])
def userinfo_me():
    """模拟获取用户基本信息"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return error_response(12001, "invalid access token", 401)

    return jsonify({
        "open_id": f"mock_openid_{uuid.uuid4().hex[:24]}",
        "union_id": f"mock_unionid_{uuid.uuid4().hex[:24]}",
        "display_name": "MockUser",
        "email": "mockuser@example.com",
        "picture": "https://example.com/avatar.png",
        "locale": "zh-CN"
    }), 200


# ==================== 2. Get Privacy Records ====================
# 参考: https://developer.huawei.com/consumer/cn/doc/HMSCore-References/get-privacy-records-0000001058868980

@app.route("/healthkit/v1/privacyRecords", methods=["GET"])
def get_privacy_records():
    """
    模拟查询隐私授权记录
    Query Params: startTime, endTime, dataType, appId
    """
    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")
    data_type = request.args.get("dataType")
    app_id = request.args.get("appId")

    # 构造模拟隐私记录列表
    records = [
        {
            "recordId": str(uuid.uuid4()),
            "appId": app_id or "mock_app_id_001",
            "dataType": data_type or "com.huawei.health.step",
            "grantTime": int(time.time()) - random.randint(3600, 86400),
            "revokeTime": None,
            "status": "GRANTED",
            "source": "USER_CONSENT"
        },
        {
            "recordId": str(uuid.uuid4()),
            "appId": app_id or "mock_app_id_001",
            "dataType": "com.huawei.health.heartrate",
            "grantTime": int(time.time()) - random.randint(86400, 172800),
            "revokeTime": int(time.time()) - random.randint(3600, 86400),
            "status": "REVOKED",
            "source": "USER_CONSENT"
        }
    ]

    return success_response(data={
        "privacyRecords": records,
        "totalNum": len(records)
    })


# ==================== 3. Cancel Scopes ====================
# 参考: https://developer.huawei.com/consumer/cn/doc/HMSCore-References/cancel-scopes-0000001059462192

@app.route("/healthkit/v1/scopes/cancel", methods=["POST"])
def cancel_scopes():
    """
    模拟取消授权范围
    Body JSON: { "scopes": ["scope1", "scope2"], "openId": "xxx" }
    """
    body = request.get_json(silent=True) or {}
    scopes = body.get("scopes", [])
    open_id = body.get("openId")

    if not scopes:
        return error_response(12002, "missing required parameter: scopes")
    if not open_id:
        return error_response(12002, "missing required parameter: openId")

    # 模拟取消结果
    cancelled = []
    failed = []
    for scope in scopes:
        # 随机模拟部分成功/失败
        if random.random() > 0.1:
            cancelled.append(scope)
        else:
            failed.append({"scope": scope, "reason": "scope not granted"})

    return success_response(data={
        "cancelledScopes": cancelled,
        "failedScopes": failed,
        "openId": open_id
    })





# ==============================================================================
# 通用工具函数
# ==============================================================================

def error_response(http_status, error_code, error_msg):
    """
    构造统一错误响应。
    ⚠️ 歧义#1: 文档未定义错误Body格式，此处采用华为云REST API常见格式。
    """
    body = {
        "errorCode": str(error_code),
        "errorMsg": error_msg
    }
    resp = jsonify(body)
    resp.status_code = http_status
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


def make_data_collector_id(data_type_name, prefix="derived"):
    """根据数据类型生成稳定的 dataCollectorId (Base64编码风格)"""
    raw = f"{prefix}:{data_type_name}:mock_collector_001"
    return base64.b64encode(raw.encode()).decode()


def make_original_data_collector_id(data_type_name):
    """根据数据类型生成稳定的 originalDataCollectorId"""
    return make_data_collector_id(data_type_name, prefix="raw")


def make_health_record_id(data_type_name, start_ns):
    """生成健康记录 ID"""
    raw = f"raw:{data_type_name}:mock:{start_ns}"
    return base64.b64encode(raw.encode()).decode()


# ==============================================================================
# 数据类型配置表: fieldName、值类型、值范围
# ==============================================================================

# sampleSet:polymerize 支持的数据类型
SAMPLESET_FIELD_CONFIG = {
    "com.huawei.continuous.steps.delta": {
        "fields": [
            {"fieldName": "steps_delta", "type": "integerValue", "min": 10, "max": 200}
        ],
        "is_continuous": True,
        "num_points": (2, 4),  # 连续型生成2-4个采样点
    },
    "com.huawei.instantaneous.body_weight": {
        "fields": [
            {"fieldName": "body_weight",          "type": "floatValue",   "min": 50.0,  "max": 90.0},
            {"fieldName": "bmi",                  "type": "floatValue",   "min": 18.0,  "max": 30.0},
            {"fieldName": "body_fat",             "type": "floatValue",   "min": 8.0,   "max": 25.0},
            {"fieldName": "body_fat_rate",        "type": "floatValue",   "min": 10.0,  "max": 35.0},
            {"fieldName": "muscle_mass",          "type": "floatValue",   "min": 35.0,  "max": 65.0},
            {"fieldName": "basal_metabolism",     "type": "floatValue",   "min": 1200.0,"max": 2000.0},
            {"fieldName": "moisture",             "type": "floatValue",   "min": 30.0,  "max": 45.0},
            {"fieldName": "moisture_rate",        "type": "floatValue",   "min": 45.0,  "max": 65.0},
            {"fieldName": "visceral_fat_level",   "type": "floatValue",   "min": 5.0,   "max": 15.0},
            {"fieldName": "bone_salt",            "type": "floatValue",   "min": 2.0,   "max": 4.0},
            {"fieldName": "protein_rate",         "type": "floatValue",   "min": 14.0,  "max": 22.0},
            {"fieldName": "body_age",             "type": "integerValue", "min": 18,    "max": 60},
            {"fieldName": "body_score",           "type": "floatValue",   "min": 50.0,  "max": 95.0},
            {"fieldName": "skeletal_musclel_mass","type": "floatValue",   "min": 18.0,  "max": 40.0},
            {"fieldName": "impedance",            "type": "floatValue",   "min": 300.0, "max": 800.0},
        ],
        "is_continuous": False,
        "num_points": (1, 1),
    },
    "com.huawei.instantaneous.height": {
        "fields": [
            {"fieldName": "height", "type": "floatValue", "min": 1.50, "max": 1.95},
        ],
        "is_continuous": False,
        "num_points": (1, 1),
    },
    "com.huawei.instantaneous.blood_glucose": {
        "fields": [
            {"fieldName": "level",        "type": "floatValue",   "min": 3.5, "max": 12.0},
            {"fieldName": "measure_time", "type": "integerValue", "min": 1,   "max": 9},
        ],
        "is_continuous": False,
        "num_points": (1, 2),
        "has_metadata": True,
        "metadata_template": '{"mIsConfirmed":%s}',
    },
    "com.huawei.instantaneous.blood_pressure": {
        "fields": [
            {"fieldName": "systolic_pressure",        "type": "floatValue",   "min": 90.0,  "max": 160.0},
            {"fieldName": "diastolic_pressure",       "type": "floatValue",   "min": 55.0,  "max": 100.0},
            {"fieldName": "sphygmus",                 "type": "floatValue",   "min": 55.0,  "max": 100.0},
            {"fieldName": "measurement_anomaly_flag", "type": "integerValue", "min": 1,     "max": 4},
            {"fieldName": "before_measure_activities","type": "stringValue",  "values": ["[6]", "[1,10]", "[3]", "[1,2]"]},
        ],
        "is_continuous": False,
        "num_points": (1, 2),
    },
}

# healthRecords 支持的数据类型
HEALTHRECORDS_CONFIG = {
    "com.huawei.health.record.sleep": {
        "fields": [
            {"fieldName": "fall_asleep_time",    "type": "longValue",    "derived": "start_ms"},
            {"fieldName": "wakeup_time",         "type": "longValue",    "derived": "end_ms"},
            {"fieldName": "all_sleep_time",      "type": "integerValue", "min": 180, "max": 540},
            {"fieldName": "light_sleep_time",    "type": "integerValue", "min": 100, "max": 280},
            {"fieldName": "deep_sleep_time",     "type": "integerValue", "min": 60,  "max": 180},
            {"fieldName": "dream_time",          "type": "integerValue", "min": 40,  "max": 120},
            {"fieldName": "awake_time",          "type": "integerValue", "min": 10,  "max": 60},
            {"fieldName": "wakeup_count",        "type": "integerValue", "min": 0,   "max": 5},
            {"fieldName": "deep_sleep_part",     "type": "integerValue", "min": 60,  "max": 100},
            {"fieldName": "sleep_score",         "type": "integerValue", "min": 60,  "max": 98},
            {"fieldName": "go_bed_time",         "type": "longValue",    "derived": "start_ms_minus_20min"},
            {"fieldName": "prepare_sleep_time",  "type": "longValue",    "derived": "start_ms_minus_10min"},
            {"fieldName": "off_bed_time",        "type": "longValue",    "derived": "start_ms_minus_5min"},
            {"fieldName": "sleep_type",          "type": "integerValue", "min": 1,   "max": 1},  # 默认科学睡眠
        ],
        "sub_data_types": {
            "com.huawei.continuous.sleep.fragment": {
                "fields": [
                    {"fieldName": "sleep_state", "type": "integerValue", "values": [1, 3, 4, 2, 1]},
                ],
            },
            "com.huawei.sleep.on_off_bed_record": {
                "fields": [
                    {"fieldName": "onOffBedState", "type": "integerValue", "values": [1, 2, 1, 2]},
                ],
            },
        },
    },
    "com.huawei.continuous.ecg_record": {
        "fields": [
            {"fieldName": "ecg_type",                "type": "integerValue", "min": 1,    "max": 1},
            {"fieldName": "avg_heart_rate",          "type": "floatValue",   "min": 60.0, "max": 90.0},
            {"fieldName": "ecg_arrhythmia_type",     "type": "longValue",    "min": 0,    "max": 0},
            {"fieldName": "user_symptom",            "type": "longValue",    "min": 0,    "max": 0},
            {"fieldName": "sampling_frequency",      "type": "integerValue", "min": 0,    "max": 0},
            {"fieldName": "ecg_algorithm_version",   "type": "stringValue",  "fixed": "1.0"},
        ],
        "sub_data_relation": [
            {
                "dataTypeName": "com.huawei.continuous.ecg_detail",
            }
        ],
    },
}

# 30 天毫秒上限
THIRTY_DAYS_MS = 30 * 24 * 3600 * 1000
# 31 天纳秒上限
THIRTY_ONE_DAYS_NS = 31 * 24 * 3600 * 1_000_000_000
# 最早合法时间戳 (2014-01-01 00:00:00 UTC)
EARLIEST_MS = 1388505600000


# ==============================================================================
# 接口一: POST /healthkit/v2/sampleSet:polymerize
# ==============================================================================

@app.route("/healthkit/v2/sampleSet:polymerize", methods=["POST"])
def sampleset_polymerize():
    """
    采样数据明细查询
    文档: https://developer.huawei.com/consumer/cn/doc/HMSCore-References/sampleset_polymerize_detailed-0000001050114864
    """
    # ---------- 解析请求体 ----------
    body = request.get_json(silent=True)
    if body is None:
        return error_response(400, "SC_BAD_REQUEST", "Request body must be valid JSON")

    start_time = body.get("startTime")       # Long, 可选, 毫秒
    end_time = body.get("endTime")           # Long, 必选, 毫秒
    polymerize_with = body.get("polymerizeWith")  # List, 必选

    # ---------- 参数校验 ----------
    if end_time is None:
        return error_response(400, "12002", "missing required parameter: endTime")

    if polymerize_with is None or not isinstance(polymerize_with, list) or len(polymerize_with) == 0:
        return error_response(400, "12002", "missing required parameter: polymerizeWith")

    if len(polymerize_with) > 20:
        return error_response(400, "12003", "polymerizeWith list exceeds maximum size of 20")

    # ⚠️ 歧义#3: startTime 可选，但约束要求 endTime > startTime
    if start_time is not None:
        if not isinstance(start_time, (int, float)):
            return error_response(400, "12003", "startTime must be a numeric value (milliseconds)")
        if start_time < EARLIEST_MS:
            return error_response(400, "12003", f"startTime must not be earlier than {EARLIEST_MS} (2014-01-01)")
        if end_time <= start_time:
            return error_response(400, "12003", "endTime must be greater than startTime")
        if (end_time - start_time) > THIRTY_DAYS_MS:
            return error_response(400, "12003", "time interval exceeds 30 days")

    if not isinstance(end_time, (int, float)):
        return error_response(400, "12003", "endTime must be a numeric value (milliseconds)")

    # ---------- 生成模拟数据 ----------
    # 如果 startTime 未提供，默认取 endTime 前24小时
    effective_start = start_time if start_time is not None else (end_time - 24 * 3600 * 1000)

    groups = []
    for pw in polymerize_with:
        data_type_name = pw.get("dataTypeName")
        data_collector_id_query = pw.get("dataCollectorId")

        # 至少需要一个聚合标识
        if not data_type_name and not data_collector_id_query:
            return error_response(400, "12003",
                "each polymerizeWith item must have at least dataTypeName or dataCollectorId")

        # 如果未指定 dataTypeName，从 dataCollectorId 推断 (Mock: 默认步数)
        if not data_type_name:
            data_type_name = "com.huawei.continuous_steps.delta"

        config = SAMPLESET_FIELD_CONFIG.get(data_type_name)
        if config is None:
            # ⚠️ 歧义#5 类似处理: 未知数据类型返回空采样点而非报错
            config = {
                "fields": [{"fieldName": "unknown_field", "type": "integerValue", "min": 0, "max": 0}],
                "is_continuous": False,
                "num_points": (1, 1),
            }

        # 构造采样点
        num_points = random.randint(*config["num_points"])
        sample_points = []

        time_span_ns = (end_time - effective_start) * 1_000_000  # ms → ns
        point_interval = time_span_ns // max(num_points, 1)

        for i in range(num_points):
            pt_start_ns = int(effective_start * 1_000_000) + i * point_interval

            if config["is_continuous"]:
                # 连续型: endTime > startTime (1~10 分钟跨度)
                pt_end_ns = pt_start_ns + random.randint(60_000_000_000, 600_000_000_000)
            else:
                # 瞬时型: endTime == startTime
                pt_end_ns = pt_start_ns

            # 构造 value 列表
            values = []
            for field_def in config["fields"]:
                val_obj = {"fieldName": field_def["fieldName"]}
                if field_def["type"] == "floatValue":
                    val_obj["floatValue"] = round(random.uniform(field_def["min"], field_def["max"]), 1)
                elif field_def["type"] == "integerValue":
                    val_obj["integerValue"] = random.randint(field_def["min"], field_def["max"])
                elif field_def["type"] == "longValue":
                    val_obj["longValue"] = random.randint(field_def["min"], field_def["max"])
                elif field_def["type"] == "stringValue":
                    if "fixed" in field_def:
                        val_obj["stringValue"] = field_def["fixed"]
                    elif "values" in field_def:
                        val_obj["stringValue"] = random.choice(field_def["values"])
                    else:
                        val_obj["stringValue"] = ""
                values.append(val_obj)

            sp = {
                "startTime": pt_start_ns,
                "endTime": pt_end_ns,
                "dataTypeName": data_type_name,
                "originalDataCollectorId": make_original_data_collector_id(data_type_name),
                "value": values,
            }

            # metadata 处理
            if config.get("has_metadata"):
                confirmed = random.choice(["true", "false"])
                sp["metadata"] = config["metadata_template"] % confirmed

            sample_points.append(sp)

        # ⚠️ 歧义#4: 示例6中 SampleSet 包含 startTime/endTime/timeZone
        # 此处始终包含这些额外字段以对齐示例6
        group_entry = {
            "startTime": effective_start,
            "endTime": end_time,
            "sampleSet": [
                {
                    "dataCollectorId": make_data_collector_id(data_type_name),
                    "samplePoints": sample_points,
                }
            ],
        }
        groups.append(group_entry)

    # ---------- 构造响应 ----------
    response = jsonify({"group": groups})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["x-health-app-privacy"] = "1"
    return response


# ==============================================================================
# 接口二: GET /healthkit/v2/healthRecords
# ==============================================================================

@app.route("/healthkit/v2/healthRecords", methods=["GET"])
def health_records():
    """
    查询数据类型的健康记录
    文档: healthRecords GET 接口
    """
    # ---------- 解析查询参数 ----------
    start_time_str = request.args.get("startTime")     # Long, 必选, 纳秒
    end_time_str = request.args.get("endTime")         # Long, 必选, 纳秒
    data_type = request.args.get("dataType")           # String, 必选

    # ⚠️ 歧义#2: subDataType 多值 — 同时支持重复参数和逗号分隔
    sub_data_types = request.args.getlist("subDataType")
    if len(sub_data_types) == 1 and "," in sub_data_types[0]:
        sub_data_types = sub_data_types[0].split(",")
    # 过滤空值
    sub_data_types = [s.strip() for s in sub_data_types if s.strip()]

    # ---------- 参数校验 ----------
    if not start_time_str:
        return error_response(400, "12002", "missing required parameter: startTime")
    if not end_time_str:
        return error_response(400, "12002", "missing required parameter: endTime")
    if not data_type:
        return error_response(400, "12002", "missing required parameter: dataType")

    try:
        start_time_ns = int(start_time_str)
        end_time_ns = int(end_time_str)
    except (ValueError, TypeError):
        return error_response(400, "12003", "startTime and endTime must be valid integers (nanoseconds)")

    if end_time_ns <= start_time_ns:
        return error_response(400, "12003", "endTime must be greater than startTime")

    if (end_time_ns - start_time_ns) > THIRTY_ONE_DAYS_NS:
        return error_response(400, "12003", "time interval exceeds 31 days")

    # ---------- 查询数据类型配置 ----------
    config = HEALTHRECORDS_CONFIG.get(data_type)
    if config is None:
        # ⚠️ 歧义#5: 不支持的 dataType — 返回空列表
        response = jsonify({"healthRecords": []})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers["x-health-app-privacy"] = "1"
        return response

    # ---------- 生成模拟健康记录 ----------
    start_ms = start_time_ns // 1_000_000
    end_ms = end_time_ns // 1_000_000

    # 构造 value
    values = []
    for field_def in config["fields"]:
        val_obj = {"fieldName": field_def["fieldName"]}
        derived = field_def.get("derived")
        if derived == "start_ms":
            val_obj["longValue"] = start_ms
        elif derived == "end_ms":
            val_obj["longValue"] = end_ms
        elif derived == "start_ms_minus_20min":
            val_obj["longValue"] = start_ms - 20 * 60 * 1000
        elif derived == "start_ms_minus_10min":
            val_obj["longValue"] = start_ms - 10 * 60 * 1000
        elif derived == "start_ms_minus_5min":
            val_obj["longValue"] = start_ms - 5 * 60 * 1000
        elif field_def["type"] == "floatValue":
            val_obj["floatValue"] = round(random.uniform(field_def["min"], field_def["max"]), 1)
        elif field_def["type"] == "integerValue":
            val_obj["integerValue"] = random.randint(field_def["min"], field_def["max"])
        elif field_def["type"] == "longValue":
            val_obj["longValue"] = random.randint(field_def["min"], field_def["max"])
        elif field_def["type"] == "stringValue":
            val_obj["stringValue"] = field_def.get("fixed", "")
        values.append(val_obj)

    # 构造健康记录
    record = {
        "startTime": start_time_ns,
        "endTime": end_time_ns,
        "dataTypeName": data_type,
        "originalDataCollectorId": make_original_data_collector_id(data_type),
        "value": values,
        "id": make_health_record_id(data_type, start_time_ns),
    }

    # ---------- subData 处理 ----------
    sub_data_config_map = config.get("sub_data_types", {})
    if sub_data_types and sub_data_config_map:
        sub_data = {}
        for sdt in sub_data_types:
            sdt_config = sub_data_config_map.get(sdt)
            if sdt_config is None:
                continue

            # 为 subData 生成采样点
            # 将时间区间分段
            time_span = end_time_ns - start_time_ns
            num_fragments = len(sdt_config["fields"][0].get("values", [1]))
            fragment_duration = time_span // max(num_fragments, 1)

            sub_sample_points = []
            for idx in range(num_fragments):
                frag_start = start_time_ns + idx * fragment_duration
                frag_end = frag_start + fragment_duration

                sp_values = []
                for field_def in sdt_config["fields"]:
                    val_obj = {"fieldName": field_def["fieldName"]}
                    if "values" in field_def:
                        val_obj[field_def["type"]] = field_def["values"][idx % len(field_def["values"])]
                    elif field_def["type"] == "integerValue":
                        val_obj["integerValue"] = random.randint(field_def["min"], field_def["max"])
                    sp_values.append(val_obj)

                sub_sample_points.append({
                    "startTime": frag_start,
                    "endTime": frag_end,
                    "dataTypeName": sdt,
                    "value": sp_values,
                })

            sub_data[sdt] = {
                "startTime": start_time_ns,
                "endTime": end_time_ns,
                "dataCollectorId": make_data_collector_id(sdt, prefix="raw"),
                "samplePoints": sub_sample_points,
            }

        if sub_data:
            record["subData"] = sub_data

    # ---------- subDataRelation 处理 ----------
    sub_data_relation = config.get("sub_data_relation")
    if sub_data_relation:
        relations = []
        for rel in sub_data_relation:
            relations.append({
                "startTime": start_time_ns,
                "endTime": end_time_ns,
                "dataTypeName": rel["dataTypeName"],
                "dataCollectorId": make_data_collector_id(rel["dataTypeName"], prefix="raw"),
            })
        record["subDataRelation"] = relations

    # ---------- 构造响应 ----------
    response = jsonify({"healthRecords": [record]})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["x-health-app-privacy"] = "1"
    return response


# ==============================================================================
# 健康检查 & 404 兜底
# ==============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Health Service Kit Mock"})


@app.errorhandler(404)
def not_found(e):
    return error_response(404, "SC_NOT_FOUND", "Service not found. Please check the request URI.")


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response(405, "SC_METHOD_NOT_ALLOWED", "HTTP Method not allowed.")




# ==================== 健康检查 & 路由索引 ====================

@app.route("/", methods=["GET"])
def index():
    """API 索引页"""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static" and rule.endpoint != "index":
            routes.append({
                "path": rule.rule,
                "methods": list(rule.methods - {"OPTIONS", "HEAD"}),
                "endpoint": rule.endpoint
            })
    return jsonify({
        "service": "HMS Core Mock API Server",
        "version": "1.0.0",
        "endpoints": sorted(routes, key=lambda x: x["path"])
    })


if __name__ == "__main__":
    print("=" * 60)
    print("  HMS Core Mock API Server")
    print("  http://localhost:5000/")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)