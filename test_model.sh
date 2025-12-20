#!/bin/bash
# 快速测试脚本

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 测试 Replicate 模型${NC}"
echo "================================"

# 检查 API token
if [ -z "$REPLICATE_API_TOKEN" ]; then
    echo -e "${RED}❌ 请设置 REPLICATE_API_TOKEN${NC}"
    echo "export REPLICATE_API_TOKEN=your_token"
    exit 1
fi

# 使用 curl 测试
echo -e "\n${GREEN}📡 发送测试请求...${NC}"

PREDICTION=$(curl -s -X POST \
  -H "Authorization: Token $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "hzeyuan/wan-model",
    "input": {
      "prompt": "你好,请介绍一下自己",
      "max_new_tokens": 256,
      "temperature": 0.7
    }
  }' \
  https://api.replicate.com/v1/predictions)

# 提取 prediction ID 和 URL
PREDICTION_ID=$(echo $PREDICTION | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
PREDICTION_URL=$(echo $PREDICTION | python3 -c "import sys, json; print(json.load(sys.stdin)['urls']['get'])" 2>/dev/null)

if [ -z "$PREDICTION_ID" ]; then
    echo -e "${RED}❌ 创建预测失败${NC}"
    echo "$PREDICTION"
    exit 1
fi

echo -e "${GREEN}✓ 预测 ID: $PREDICTION_ID${NC}"
echo -e "${BLUE}🔗 查看详情: https://replicate.com/p/$PREDICTION_ID${NC}"

# 轮询结果
echo -e "\n${BLUE}⏳ 等待结果...${NC}"

while true; do
    RESULT=$(curl -s -H "Authorization: Token $REPLICATE_API_TOKEN" $PREDICTION_URL)
    STATUS=$(echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

    echo -e "状态: ${BLUE}$STATUS${NC}"

    if [ "$STATUS" = "succeeded" ]; then
        echo -e "\n${GREEN}✓ 完成!${NC}"

        # 显示日志
        echo -e "\n${BLUE}📋 日志:${NC}"
        echo "--------------------------------"
        echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin).get('logs', ''))"
        echo "--------------------------------"

        # 显示输出
        echo -e "\n${GREEN}💬 输出:${NC}"
        echo "================================"
        echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin).get('output', ''))"
        echo "================================"

        # 显示性能
        echo -e "\n${BLUE}📊 性能:${NC}"
        echo $RESULT | python3 -c "import sys, json; metrics = json.load(sys.stdin).get('metrics', {}); print(f\"预测时间: {metrics.get('predict_time', 'N/A')}s\")"

        break
    elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "canceled" ]; then
        echo -e "\n${RED}❌ 失败${NC}"
        echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', ''))"
        break
    fi

    sleep 2
done
