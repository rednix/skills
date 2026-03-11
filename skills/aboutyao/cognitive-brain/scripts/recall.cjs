#!/usr/bin/env node
/**
 * Cognitive Brain - 记忆检索脚本
 * 从记忆系统中检索相关信息
 */

const fs = require('fs');
const path = require('path');

// 加载配置
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 解析参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    params[key] = args[i + 1];
  }
  return params;
}

// 关键词检索
async function keywordSearch(pool, query, limit = 10) {
  try {
    const result = await pool.query(`
      SELECT id, summary, content, timestamp, importance, type
      FROM episodes
      WHERE summary ILIKE $1 OR content ILIKE $1
      ORDER BY importance DESC, timestamp DESC
      LIMIT $2
    `, [`%${query}%`, limit]);
    
    return result.rows;
  } catch (e) {
    return [];
  }
}

// 联想激活检索
async function associationSearch(pool, query, limit = 10) {
  try {
    // 1. 找到查询相关的概念
    const concepts = await pool.query(`
      SELECT id, name FROM concepts 
      WHERE name ILIKE $1
      LIMIT 5
    `, [`%${query}%`]);
    
    if (concepts.rows.length === 0) return [];
    
    // 2. 激活传播
    const activated = new Map();
    const frontier = new Map();
    
    concepts.rows.forEach(c => frontier.set(c.id, { name: c.name, level: 1.0 }));
    
    const threshold = 0.3;
    const decay = 0.9;
    
    for (let depth = 0; depth < 3; depth++) {
      const newFrontier = new Map();
      
      for (const [conceptId, data] of frontier) {
        if (data.level < threshold) continue;
        
        activated.set(conceptId, data);
        
        // 沿边传播
        const edges = await pool.query(`
          SELECT c.id, c.name, a.weight 
          FROM associations a
          JOIN concepts c ON c.id = a.to_id
          WHERE a.from_id = $1
        `, [conceptId]);
        
        for (const edge of edges.rows) {
          const newLevel = data.level * decay * edge.weight;
          if (!newFrontier.has(edge.id) || newFrontier.get(edge.id).level < newLevel) {
            newFrontier.set(edge.id, { name: edge.name, level: newLevel });
          }
        }
      }
      
      frontier.clear();
      newFrontier.forEach((v, k) => frontier.set(k, v));
    }
    
    // 3. 用激活的概念检索记忆
    const conceptNames = [...activated.values()].map(a => a.name);
    
    if (conceptNames.length === 0) return [];
    
    const placeholders = conceptNames.map((_, i) => `$${i + 1}`).join(',');
    
    const result = await pool.query(`
      SELECT DISTINCT e.id, e.summary, e.content, e.timestamp, e.importance, e.type
      FROM episodes e
      WHERE EXISTS (
        SELECT 1 FROM json_array_elements_text(e.entities) entity
        WHERE entity IN (${placeholders})
      )
      ORDER BY e.importance DESC
      LIMIT $${conceptNames.length + 1}
    `, [...conceptNames, limit]);
    
    return result.rows;
  } catch (e) {
    return [];
  }
}

// 混合检索
async function hybridSearch(pool, query, options = {}) {
  const limit = options.limit || 10;
  
  const keywordResults = await keywordSearch(pool, query, limit);
  const assocResults = await associationSearch(pool, query, limit);
  
  // 合并去重
  const merged = new Map();
  
  keywordResults.forEach((r, i) => {
    merged.set(r.id, { 
      ...r, 
      score: (limit - i) / limit * 0.4,
      source: 'keyword'
    });
  });
  
  assocResults.forEach((r, i) => {
    if (merged.has(r.id)) {
      merged.get(r.id).score += (limit - i) / limit * 0.6;
      merged.get(r.id).source = 'hybrid';
    } else {
      merged.set(r.id, { 
        ...r, 
        score: (limit - i) / limit * 0.6,
        source: 'association'
      });
    }
  });
  
  // 排序返回
  return [...merged.values()]
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

// 从文件检索（后备方案）
function searchFromFile(query, limit = 10) {
  const memoryFile = path.join(__dirname, '..', 'data', 'memories.jsonl');
  
  if (!fs.existsSync(memoryFile)) {
    return [];
  }
  
  const lines = fs.readFileSync(memoryFile, 'utf8').split('\n').filter(Boolean);
  const memories = lines.map(line => JSON.parse(line));
  
  const results = memories
    .filter(m => 
      m.summary?.includes(query) || 
      m.content?.includes(query) ||
      m.entities?.some(e => e.includes(query))
    )
    .sort((a, b) => b.importance - a.importance)
    .slice(0, limit);
  
  return results;
}

// 主函数
async function recall(query, options = {}) {
  let results = [];
  let source = 'file';
  
  try {
    const pg = require('pg');
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    results = await hybridSearch(pool, query, options);
    source = 'postgresql';
    
    // 更新访问计数
    for (const r of results) {
      await pool.query(`
        UPDATE episodes 
        SET access_count = access_count + 1, last_accessed = NOW()
        WHERE id = $1
      `, [r.id]);
    }
    
    await pool.end();
  } catch (e) {
    results = searchFromFile(query, options.limit);
  }
  
  return {
    query,
    results,
    total: results.length,
    source,
    timestamp: new Date().toISOString()
  };
}

// 执行
async function main() {
  const params = parseArgs();
  
  if (!params.query) {
    console.log('用法: node recall.cjs --query "关键词" [--options \'{"limit":5}\' ]');
    console.log('\n示例:');
    console.log('  node recall.cjs --query "项目"');
    console.log('  node recall.cjs --query "Alpha" --options \'{"limit":3}\'');
    process.exit(1);
  }
  
  const options = params.options ? JSON.parse(params.options) : {};
  
  console.log(`🔍 检索: "${params.query}"\n`);
  
  const result = await recall(params.query, options);
  
  console.log(`✅ 找到 ${result.total} 条记忆 (来源: ${result.source})\n`);
  
  result.results.forEach((r, i) => {
    console.log(`[${i + 1}] ${r.summary.slice(0, 50)}...`);
    console.log(`    类型: ${r.type} | 重要性: ${r.importance?.toFixed(2) || 'N/A'}`);
    console.log(`    时间: ${r.timestamp || r.created_at}`);
    if (r.score) console.log(`    相关度: ${(r.score * 100).toFixed(1)}%`);
    console.log();
  });
}

main();
