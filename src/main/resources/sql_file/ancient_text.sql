/*
 Navicat Premium Data Transfer

 Source Server         : pcd
 Source Server Type    : MySQL
 Source Server Version : 80041
 Source Host           : localhost:3306
 Source Schema         : gujihuohua

 Target Server Type    : MySQL
 Target Server Version : 80041
 File Encoding         : 65001

 Date: 04/12/2025 16:25:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ancient_text
-- ----------------------------
DROP TABLE IF EXISTS `ancient_text`;
CREATE TABLE `ancient_text`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '古籍标题/文件名',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '类别(史书/志书等)',
  `raw_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '原始TXT文件路径',
  `json_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '处理后JSON文件路径',
  `sentence_count` int NULL DEFAULT 0 COMMENT '总句数',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '古籍语料表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of ancient_text
-- ----------------------------
INSERT INTO `ancient_text` VALUES (1, '史记—高祖本纪', '史书', '2025-11-21/史记—高祖本纪_20251121_102455.txt', '2025-11-21/史记—高祖本纪_20251121_102455.json', 3, '2025-11-21 10:24:55');
INSERT INTO `ancient_text` VALUES (2, '高祖', '史书', '2025-11-24/高祖_20251124_120911.txt', '2025-11-24/高祖_20251124_120911.json', 70, '2025-11-24 12:09:11');
INSERT INTO `ancient_text` VALUES (3, '十二本纪·高祖本纪第八原文', '史书', '2025-11-24/十二本纪·高祖本纪第八原文_20251124_155818.txt', '2025-11-24/十二本纪·高祖本纪第八原文_20251124_155818.json', 650, '2025-11-24 15:58:18');
INSERT INTO `ancient_text` VALUES (4, '十二本纪·高祖本纪第八原文', '史书', '2025-11-24/十二本纪·高祖本纪第八原文_20251124_161656.txt', '2025-11-24/十二本纪·高祖本纪第八原文_20251124_161656.json', 649, '2025-11-24 16:16:56');

SET FOREIGN_KEY_CHECKS = 1;
