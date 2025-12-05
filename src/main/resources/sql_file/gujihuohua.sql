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

 Date: 04/12/2025 16:26:00
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
-- Table structure for xinhua_ci
-- ----------------------------
DROP TABLE IF EXISTS `xinhua_ci`;
CREATE TABLE `xinhua_ci`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ci` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '词语',
  `explanation` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '释义',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_ci`(`ci`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 264434 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for xinhua_idiom
-- ----------------------------
DROP TABLE IF EXISTS `xinhua_idiom`;
CREATE TABLE `xinhua_idiom`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `word` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '成语',
  `pinyin` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `abbreviation` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `derivation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '出处',
  `explanation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '释义',
  `example` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '例句',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_word`(`word`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 30895 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for xinhua_word
-- ----------------------------
DROP TABLE IF EXISTS `xinhua_word`;
CREATE TABLE `xinhua_word`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `word` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '汉字',
  `oldword` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '繁体/旧字',
  `strokes` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '笔画数',
  `pinyin` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '拼音',
  `radicals` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '部首',
  `explanation` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '释义',
  `more` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '更多信息',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_word`(`word`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16142 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for xinhua_xiehouyu
-- ----------------------------
DROP TABLE IF EXISTS `xinhua_xiehouyu`;
CREATE TABLE `xinhua_xiehouyu`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `riddle` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '谜面',
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '谜底',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14032 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
