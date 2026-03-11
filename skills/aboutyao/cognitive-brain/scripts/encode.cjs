#!/usr/bin/env node
/**
 * Cognitive Brain - 记忆编码脚本
 * 将信息编码存入记忆系统
 */

const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// 加载配置
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    params[key] = args[i + 1];
  }
  
  return params;
}

// 实体提取（简化版）
function extractEntities(content) {
  const entities = [];
  
  // 匹配大写开头的词（可能的专有名词）
  const properNouns = content.match(/[A-Z][a-zA-Z]+/g) || [];
  
  // 匹配中文词组（简化）
  const chineseWords = content.match(/[\u4e00-\u9fa5]{2,}/g) || [];
  
  // 技术术语
  const techTerms = content.match(/\b(Rust|Python|JavaScript|TypeScript|AI|API|SQL|Redis|PostgreSQL|React|Vue|Node)\b/gi) || [];
  
  entities.push(...new Set([...properNouns, ...chineseWords, ...techTerms]));
  
  return entities.slice(0, 20); // 限制数量
}

// 情感分析（简化版）
function analyzeEmotion(content) {
  const positive = ['开心', '高兴', '喜欢', '棒', '好', '成功', 'great', 'good', 'love', '谢谢', '感谢'];
  const negative = ['难过', '伤心', '讨厌', '差', '失败', '错误', 'bad', 'sad', 'error', '不对', '错了'];
  const urgent = ['紧急', '马上', '立刻', 'urgent', 'asap', '赶紧'];
  
  let valence = 0;
  let arousal = 0;
  
  positive.forEach(w => { if (content.includes(w)) valence += 0.2; });
  negative.forEach(w => { if (content.includes(w)) valence -= 0.2; });
  urgent.forEach(w => { if (content.includes(w)) arousal += 0.3; });
  
  return {
    valence: Math.max(-1, Math.min(1, valence)),
    arousal: Math.max(0, Math.min(1, arousal + Math.abs(valence)))
  };
}

// 计算重要性
function calculateImportance(params) {
  const novelty = params.novelty ?? 0.5;
  const emotion = params.emotion?.valence ?? 0;
  const relevance = params.relevance ?? 0.5;
  const frequency = params.frequency ?? 0;
  
  const importance = 
    novelty * 0.3 + 
    Math.abs(emotion) * 0.3 + 
    relevance * 0.25 + 
    (1 - frequency) * 0.15;
  
  return Math.max(0, Math.min(1, importance));
}

// 选择存储层级
function selectLayer(importance) {
  if (importance >= 0.8) return ['semantic', 'episodic'];
  if (importance >= 0.5) return ['episodic'];
  if (importance >= 0.3) return ['working'];
  return ['sensory'];
}

// 主编码函数
async function encode(content, metadata = {}) {
  const id = uuidv4();
  const now = new Date().toISOString();
  
  // 1. 信息提取
  const entities = metadata.entities || extractEntities(content);
  const emotion = metadata.emotion || analyzeEmotion(content);
  const tags = metadata.tags || [];
  
  // 2. 计算重要性
  const importance = metadata.importance || calculateImportance({
    novelty: metadata.novelty,
    emotion: emotion,
    relevance: metadata.relevance,
    frequency: metadata.frequency
  });
  
  // 3. 选择存储层级
  const layers = selectLayer(importance);
  
  // 4. 生成摘要
  const summary = metadata.summary || content.slice(0, 100);
  
  // 构建记忆对象
  const memory = {
    id,
    timestamp: now,
    type: metadata.type || 'observation',
    summary,
    content,
    entities,
    emotion,
    tags,
    importance,
    layers,
    created_at: now
  };
  
  // 5. 存储到数据库
  try {
    const pg = require('pg');
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    if (layers.includes('episodic')) {
      await pool.query(`
        INSERT INTO episodes (id, type, summary, content, entities, emotions, tags, importance)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      `, [
        id,
        memory.type,
        memory.summary,
        memory.content,
        JSON.stringify(memory.entities),
        JSON.stringify(memory.emotion),
        JSON.stringify(memory.tags),
        memory.importance
      ]);
      
      // 建立联想
      for (const entity of entities) {
        // 确保概念存在
        await pool.query(`
          INSERT INTO concepts (name, type, importance)
          VALUES ($1, 'entity', $2)
          ON CONFLICT (name) DO UPDATE SET
            importance = GREATEST(concepts.importance, $2),
            last_accessed = NOW()
        `, [entity, memory.importance]);
      }
    }
    
    await pool.end();
  } catch (e) {
    // 如果数据库不可用，输出到文件
    const memoryFile = path.join(__dirname, '..', 'data', 'memories.jsonl');
    const dataDir = path.dirname(memoryFile);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    fs.appendFileSync(memoryFile, JSON.stringify(memory) + '\n');
  }
  
  return memory;
}

// 主函数
async function main() {
  const params = parseArgs();
  
  if (!params.content) {
    console.log('用法: node encode.cjs --content "内容" [--metadata \'{"type":"fact"}\']');
    console.log('\n示例:');
    console.log('  node encode.cjs --content "用户的项目叫Alpha" --metadata \'{"importance":0.8}\'');
    process.exit(1);
  }
  
  const metadata = params.metadata ? JSON.parse(params.metadata) : {};
  
  console.log('🧠 编码记忆...\n');
  
  const result = await encode(params.content, metadata);
  
  console.log('✅ 编码完成:');
  console.log(`   ID: ${result.id}`);
  console.log(`   类型: ${result.type}`);
  console.log(`   重要性: ${result.importance.toFixed(2)}`);
  console.log(`   层级: ${result.layers.join(', ')}`);
  console.log(`   实体: ${result.entities.slice(0, 5).join(', ')}${result.entities.length > 5 ? '...' : ''}`);
  console.log(`   情感: valence=${result.emotion.valence.toFixed(2)}, arousal=${result.emotion.arousal.toFixed(2)}`);
}

main();
