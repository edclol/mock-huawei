# ─── 示例1: 查询步数采样明细 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.continuous.steps.delta"}
    ],
    "startTime": 1789027200000,
    "endTime": 1789113600000
  }' | python3 -m json.tool


# ─── 示例2: 查询体重采样明细 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.instantaneous.body_weight"}
    ],
    "startTime": 1789027200000,
    "endTime": 1789113600000
  }' | python3 -m json.tool


# ─── 示例3: 查询身高采样明细 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.instantaneous.height"}
    ],
    "startTime": 1789027200000,
    "endTime": 1789113600000
  }' | python3 -m json.tool


# ─── 示例4: 查询血糖采样明细 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.instantaneous.blood_glucose"}
    ],
    "startTime": 1789027200000,
    "endTime": 1789113600000
  }' | python3 -m json.tool


# ─── 示例5: 查询血压采样明细 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.instantaneous.blood_pressure"}
    ],
    "startTime": 1789027200000,
    "endTime": 1789113600000
  }' | python3 -m json.tool


# ─── 示例6: 多类型查询 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" \
  -d '{
    "startTime": 1757433600000,
    "endTime": 1757520000000,
    "polymerizeWith": [
      {"dataTypeName": "com.huawei.instantaneous.body_weight"},
      {"dataTypeName": "com.huawei.instantaneous.height"},
      {"dataTypeName": "com.huawei.instantaneous.blood_glucose"},
      {"dataTypeName": "com.huawei.instantaneous.blood_pressure"}
    ]
  }' | python3 -m json.tool


# ─── 示例1: 查询睡眠健康记录（含分段明细）───
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1789027200000000000&\
endTime=1789113600000000000&\
dataType=com.huawei.health.record.sleep&\
subDataType=com.huawei.continuous.sleep.fragment" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" | python3 -m json.tool


# ─── 示例2: 查询零星小睡健康记录 ───
# (同一接口，不同时间范围模拟零星小睡)
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1789059600000000000&\
endTime=1789061400000000000&\
dataType=com.huawei.health.record.sleep&\
subDataType=com.huawei.continuous.sleep.fragment" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" | python3 -m json.tool


# ─── 示例3: 查询 ECG 心电健康记录 ───
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1789027200000000000&\
endTime=1789113600000000000&\
dataType=com.huawei.continuous.ecg_record" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Authorization: Bearer mock_access_token" | python3 -m json.tool



# ─── 缺少 endTime ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json" \
  -d '{"polymerizeWith": [{"dataTypeName": "com.huawei.continuous.steps.delta"}]}' \
  | python3 -m json.tool

# ─── endTime <= startTime ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json" \
  -d '{
    "startTime": 1789113600000,
    "endTime": 1789027200000,
    "polymerizeWith": [{"dataTypeName": "com.huawei.continuous.steps.delta"}]
  }' | python3 -m json.tool

# ─── 时间间隔超过30天 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json" \
  -d '{
    "startTime": 1700000000000,
    "endTime": 1789113600000,
    "polymerizeWith": [{"dataTypeName": "com.huawei.continuous.steps.delta"}]
  }' | python3 -m json.tool

# ─── polymerizeWith 为空 ───
curl -X POST http://localhost:5000/healthkit/v2/sampleSet:polymerize \
  -H "Content-Type: application/json" \
  -d '{"endTime": 1789113600000, "polymerizeWith": []}' \
  | python3 -m json.tool

# ─── healthRecords 缺少 dataType ───
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1789027200000000000&endTime=1789113600000000000" \
  -H "Content-Type: application/json" | python3 -m json.tool

# ─── healthRecords 时间间隔超31天 ───
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1700000000000000000&endTime=1789113600000000000&\
dataType=com.huawei.health.record.sleep" \
  -H "Content-Type: application/json" | python3 -m json.tool

# ─── 不支持的 dataType (返回空列表) ───
curl -X GET "http://localhost:5000/healthkit/v2/healthRecords?\
startTime=1789027200000000000&endTime=1789113600000000000&\
dataType=com.huawei.unknown.type" \
  -H "Content-Type: application/json" | python3 -m json.tool

# ─── 404 兜底 ───
curl -X GET http://localhost:5000/healthkit/v2/nonexistent | python3 -m json.tool

