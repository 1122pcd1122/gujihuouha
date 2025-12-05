package com.example.gujihuohua.service;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.example.gujihuohua.entity.RelationFact;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AiModelService {

    private final RestTemplate restTemplate;

    // Python 服务地址 (NER端口 5001, REL端口 5000，根据你实际情况调整)
    private final String NER_URL = "http://localhost:5001/predict";
    private final String REL_URL = "http://localhost:5000/predict";

    /**
     * 【核心流水线 - 双向探测版】
     * 改进策略：
     * 1. 遇到 nh-nh (人对人)，不再强制顺序，而是双向探测 (A->B 和 B->A 都算)。
     * 2. 遇到 nh-n (人对物)，依然强制 nh 为主 (规则过滤)。
     */
    public List<RelationFact> autoExtractPipeline(String text) {
        List<RelationFact> resultFacts = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) return resultFacts;

        // 1. 调用 NER
        JSONObject nerRes = predictNer(text);
        if (nerRes == null || nerRes.getInteger("code") != 200) return resultFacts;

        // 2. 提取实体
        List<Map<String, String>> entities = new ArrayList<>();
        JSONObject entityMap = nerRes.getJSONObject("data").getJSONObject("entities");
        if (entityMap != null) {
            for (String type : entityMap.keySet()) {
                JSONArray words = entityMap.getJSONArray(type);
                for (Object w : words) {
                    Map<String, String> e = new HashMap<>();
                    e.put("word", (String) w);
                    e.put("type", type);
                    entities.add(e);
                }
            }
        }
        if (entities.size() < 2) return resultFacts;

        // 3. 双重循环 (全排列)
        // 注意：这里去掉了 j = i + 1，改回全排列，但在内部做剪枝
        for (int i = 0; i < entities.size(); i++) {
            for (int j = 0; j < entities.size(); j++) {
                if (i == j) continue; // 跳过自己

                Map<String, String> sub = entities.get(i);
                Map<String, String> obj = entities.get(j);

                if ("TIME".equals(sub.get("type")) || "TIME".equals(obj.get("type"))) {
                    continue;
                }

                String subPos = mapNerTypeToRelPos(sub.get("type"));
                String objPos = mapNerTypeToRelPos(obj.get("type"));

                // === 策略优化区 ===

                // 策略 1: 如果两个都是人 (nh vs nh)
                // -> 允许双向预测。因为 "项羽"->"刘邦"(对手) 和 "刘邦"->"项羽"(对手) 都是成立的。
                // -> 或者 "刘邦"->"刘盈"(父子)，反过来 "刘盈"->"刘邦" (无关系/子父)。
                // -> 所以这里不做 continue，直接放行，让 AI 决定。
                if ("nh".equals(subPos) && "nh".equals(objPos)) {
                    // 放行，不做处理
                }

                // 策略 2: 如果是一人一物 (nh vs n/ns)
                // -> 强制要求 主体必须是 nh (人)。如果当前循环的主体不是人，直接跳过。
                else if ("nh".equals(subPos)) {
                    // 主体是人，客体是物 -> 放行
                }
                else if ("nh".equals(objPos)) {
                    // 主体是物，客体是人 -> 不符合古文语法习惯（通常人是施动者），跳过！
                    // 例如：不要预测 "咸阳(ns) -> 占领 -> 刘邦(nh)"
                    continue;
                }

                // 策略 3: 物对物 (n vs n)
                // -> 直接跳过
                else {
                    continue;
                }

                // === 发送请求 ===
                RelationFact fact = new RelationFact();
                fact.setText(text);
                fact.setSubjectWord(sub.get("word"));
                fact.setSubjectPos(subPos);
                fact.setObjectWord(obj.get("word"));
                fact.setObjectPos(objPos);

                JSONObject relRes = predictRelationForSingle(fact);

                if (relRes != null && "success".equals(relRes.getString("status"))) {
                    String relation = relRes.getJSONObject("data").getString("predicted_relation");

                    // 只有模型明确说"有关系"，我们才收录
                    if (isValidRelation(relation)) {
                        fact.setPredicate(relation);
                        resultFacts.add(fact);
                    }
                }
            }
        }
        return resultFacts;
    }

    private String mapNerTypeToRelPos(String nerType) {
        if (nerType == null) return "n";
        switch (nerType.toUpperCase()) {
            case "PER": return "nh";
            case "LOC": return "ns";
            default: return "n";
        }
    }

    /**
     * 单句关系预测 (底层调用)
     */
    public JSONObject predictRelationForSingle(RelationFact fact) {
        Map<String, Object> params = new HashMap<>();
        params.put("text", fact.getText());
        params.put("subject_word", fact.getSubjectWord());
        params.put("subject_pos", fact.getSubjectPos());
        params.put("object_word", fact.getObjectWord());
        params.put("object_pos", fact.getObjectPos());

        return sendPost(REL_URL, params);
    }


    // 统一发送 POST 请求
    private JSONObject sendPost(String url, Map<String, ?> params) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> request = new HttpEntity<>(JSON.toJSONString(params), headers);
        try {
            String response = restTemplate.postForObject(url, request, String.class);
            return JSON.parseObject(response);
        } catch (Exception e) {
            // e.printStackTrace();
            // 生产环境可以注释掉打印，防止刷屏
            return null;
        }
    }

    // 调用 NER 的简易封装
    private JSONObject callApi(String url, String text) {
        return sendPost(url, java.util.Collections.singletonMap("text", text));
    }

    public JSONObject predictNer(String text) {
        return callApi(NER_URL, text);
    }

    /**
     * 【过滤器】判断关系是否有效
     * 在这里添加所有代表"没有关系"的标签
     */
    private boolean isValidRelation(String relation) {
        if (relation == null || relation.trim().isEmpty()) return false;

        // 黑名单列表 (根据你的模型实际输出进行增删)
        return !relation.equals("无关系")
                && !relation.equals("未知")
                && !relation.equals("unknown")
                && !relation.equals("no_relation")
                && !relation.equals("O")
                && !relation.equals("其他");
    }
    // 兼容旧代码的方法占位 (如果其他地方用到了)
    public String predictRelation(RelationFact fact) {
        JSONObject res = predictRelationForSingle(fact);
        if (res != null && "success".equals(res.getString("status"))) {
            return res.getJSONObject("data").getString("predicted_relation");
        }
        return null;
    }
}