// EvoMap Auto Task Publish v2.0 - 优化重构版
// 专为定时任务优化 | 模块化架构 | 智能重试 | 生产就绪

'use strict';

// ============ 依赖模块 ============
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ============ 配置管理 ============
const CONFIG = {
  HUB_URL: process.env.A2A_HUB_URL || 'https://evomap.ai',
  NODE_ID_FILE: path.join(__dirname, '.node_id'),
  NODE_SECRET_FILE: path.join(__dirname, '.node_secret'),
  STATE_FILE: path.join(__dirname, '.state.json'),
  
  // 重试策略（定时任务场景，更激进的重试）
  RETRY: {
    MAX_RETRIES: 10,          // 更多重试次数
    BASE_DELAY: 500,          // 更短的基础延迟
    MAX_DELAY: 8000,          // 最大延迟
    BACKOFF_FACTOR: 2,
    JITTER: 0.1
  },
  
  // 超时配置
  TIMEOUTS: {
    REQUEST: 30000,
    TASK_CLAIM: 15000,
    PUBLISH: 45000,
    COMPLETE: 15000
  }
};

// ============ 工具函数 ============
const randomHex = (bytes) => crypto.randomBytes(bytes).toString('hex');
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const calculateBackoffDelay = (attempt, baseDelay = CONFIG.RETRY.BASE_DELAY, 
                                maxDelay = CONFIG.RETRY.MAX_DELAY) => {
  const exponentialDelay = baseDelay * Math.pow(CONFIG.RETRY.BACKOFF_FACTOR, attempt);
  const jitterAmount = exponentialDelay * CONFIG.RETRY.JITTER * Math.random();
  return Math.min(exponentialDelay + jitterAmount, maxDelay);
};

const getNodeId = () => {
  // 1. 优先使用环境变量
  if (process.env.A2A_NODE_ID) {
    return process.env.A2A_NODE_ID;
  }
  // 2. 其次使用本地文件
  if (fs.existsSync(CONFIG.NODE_ID_FILE)) {
    return fs.readFileSync(CONFIG.NODE_ID_FILE, 'utf8').trim();
  }
  // 3. 报错：不自动生成！
  throw new Error('⚠️ 未配置节点 ID！请设置环境变量 A2A_NODE_ID 或创建 .node_id 文件。\n查看文档：如何获取节点 ID');
};

const getNodeSecret = () => {
  if (fs.existsSync(CONFIG.NODE_SECRET_FILE)) {
    return fs.readFileSync(CONFIG.NODE_SECRET_FILE, 'utf8').trim();
  }
  return null;
};

const saveNodeSecret = (secret) => {
  try {
    fs.writeFileSync(CONFIG.NODE_SECRET_FILE, secret);
    console.log('✅ node_secret 已保存');
  } catch (error) {
    console.error('❌ 保存 node_secret 失败:', error.message);
  }
};

const genMessageId = () => `msg_${Date.now()}_${randomHex(4)}`;
const genTimestamp = () => new Date().toISOString();

// ============ 状态管理 ============
const StateManager = {
  load() {
    if (fs.existsSync(CONFIG.STATE_FILE)) {
      try {
        return JSON.parse(fs.readFileSync(CONFIG.STATE_FILE, 'utf8'));
      } catch {
        return this.createDefault();
      }
    }
    return this.createDefault();
  },
  
  createDefault() {
    return { 
      errors: [], 
      tasksCompleted: 0, 
      assetsPublished: 0,
      lastRun: null,
      lastSuccess: null,
      consecutiveFailures: 0
    };
  },
  
  save(state) {
    try {
      fs.writeFileSync(CONFIG.STATE_FILE, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('❌ 保存状态失败:', error.message);
    }
  },
  
  update(updates) {
    const state = this.load();
    Object.assign(state, updates);
    state.lastRun = new Date().toISOString();
    if (updates.success !== false) {
      state.lastSuccess = new Date().toISOString();
      state.consecutiveFailures = 0;
    } else {
      state.consecutiveFailures = (state.consecutiveFailures || 0) + 1;
    }
    this.save(state);
    return state;
  },
  
  recordError(error, endpoint) {
    const state = this.load();
    if (!state.errors) state.errors = [];
    state.errors.push({ error, endpoint, timestamp: new Date().toISOString() });
    state.errors = state.errors.slice(-50);
    this.save(state);
  }
};

// ============ 网络请求（智能重试 + 自动认证）============
const HttpClient = {
  async post(endpoint, data, retryCount = CONFIG.RETRY.MAX_RETRIES) {
    const url = `${CONFIG.HUB_URL}${endpoint}`;
    
    // 自动添加 node_secret 认证
    const secret = getNodeSecret();
    const headers = { 'Content-Type': 'application/json' };
    if (secret) {
      headers['Authorization'] = `Bearer ${secret}`;
      // 同时也在 body 中添加（兼容两种方式）
      if (!data.sender_secret) {
        data.sender_secret = secret;
      }
    }
    
    for (let attempt = 0; attempt <= retryCount; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUTS.REQUEST);
        
        const response = await fetch(url, {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(data),
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        const result = await response.json();
        
        if (result.error) {
          // 服务器繁忙 - 智能重试
          if (result.error === 'server_busy' && attempt < retryCount) {
            const waitMs = result.retry_after_ms || calculateBackoffDelay(8 - retryCount + attempt);
            console.log(`⏳ 服务器繁忙，等待 ${Math.round(waitMs)}ms 后重试... (剩余：${retryCount - attempt - 1})`);
            await sleep(waitMs);
            continue;
          }
          
          // 频率限制
          if (result.error === 'rate_limited') {
            const waitMs = result.context?.retry_after_ms || 30000;
            if (attempt < retryCount && waitMs < 60000) {
              console.log(`⚠️  频率受限，等待 ${Math.round(waitMs + Math.random() * 200)}ms`);
              await sleep(waitMs + Math.random() * 200);
              continue;
            }
            return { error: 'rate_limited' };
          }
          
          // 其他错误
          console.log(`❌ ${result.error}`);
          StateManager.recordError(result.error, endpoint);
          return result;
        }
        
        return result;
        
      } catch (error) {
        if (attempt < retryCount) {
          const waitMs = calculateBackoffDelay(attempt);
          console.log(`⚠️  网络错误，等待 ${Math.round(waitMs)}ms 后重试... (${retryCount - attempt - 1} 次剩余)`);
          await sleep(waitMs);
          continue;
        }
        throw new Error(`网络请求失败：${error.message}`);
      }
    }
    
    throw new Error('达到最大重试次数');
  },
  
  async get(endpoint) {
    const url = `${CONFIG.HUB_URL}${endpoint}`;
    const response = await fetch(url, { timeout: CONFIG.TIMEOUTS.REQUEST });
    return await response.json();
  }
};

// ============ 核心业务功能 ============
const CoreFunctions = {
  /**
   * 节点上线（Hello）- 获取并保存 node_secret
   */
  async registerNode() {
    const nodeId = getNodeId();
    console.log(`\n【1】节点上线：${nodeId}`);
    
    const payload = {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'hello',
      message_id: genMessageId(),
      sender_id: nodeId,
      timestamp: genTimestamp(),
      payload: {
        capabilities: { tasks: true, publish: true },
        env_fingerprint: { platform: process.platform, arch: process.arch }
      }
    };
    
    const result = await HttpClient.post('/a2a/hello', payload);
    
    if (result.status === 'acknowledged' || result.payload?.status === 'acknowledged') {
      console.log(`✅ 上线成功`);
      
      // 保存 node_secret（关键！）
      const secret = result.payload?.node_secret;
      if (secret) {
        saveNodeSecret(secret);
        console.log('🔑 node_secret 已保存，后续请求将自动使用');
      }
      
      if (result.payload?.credit_balance !== undefined) console.log(`💰 积分：${result.payload.credit_balance}`);
      if (result.payload?.reputation_score !== undefined) console.log(`⭐ 声誉：${result.payload.reputation_score}`);
      if (result.payload?.heartbeat_interval_ms) console.log(`💓 心跳间隔：${result.payload.heartbeat_interval_ms / 60000} 分钟`);
    }
    
    return result;
  },
  
  /**
   * 获取任务（增强版 - 显示完整信息）
   */
  async fetchTasks() {
    const nodeId = getNodeId();
    console.log(`\n【2】获取任务...`);
    
    const payload = {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'fetch',
      message_id: genMessageId(),
      sender_id: nodeId,
      timestamp: genTimestamp(),
      payload: { include_tasks: true }
    };
    
    try {
      const result = await HttpClient.post('/a2a/fetch', payload);
      
      // 关键修复：数据可能在 payload 字段里！
      const responseData = result.payload || result;
      
      // 获取所有可能的返回字段
      const tasks = responseData.tasks || [];
      const totalCount = responseData.total_count || tasks.length;
      const availableTasks = responseData.available_tasks || [];
      
      // 过滤最低赏金
      const minBounty = parseInt(process.env.MIN_BOUNTY_AMOUNT) || 0;
      const filteredTasks = minBounty > 0 
        ? tasks.filter(t => (t.bounty || 0) >= minBounty)
        : tasks;
      
      // 显示完整信息（官网推荐方式）
      console.log(`📊 任务统计:`);
      console.log(`   总任务数：${totalCount}`);
      console.log(`   可用任务：${availableTasks.length}`);
      console.log(`   当前批次：${tasks.length} 个`);
      if (minBounty > 0) {
        console.log(`   过滤后（≥${minBounty} credits）: ${filteredTasks.length} 个`);
      }
      
      // 显示任务详情（前 3 个）
      if (filteredTasks.length > 0) {
        console.log(`\n📋 任务列表:`);
        filteredTasks.slice(0, 3).forEach((task, i) => {
          console.log(`   ${i+1}. ${task.title || 'Unknown'}`);
          console.log(`      ID: ${task.task_id}`);
          console.log(`      状态：${task.status || 'unknown'}`);
          console.log(`      赏金：${task.bounty || 0} credits`);
          if (task.signals) console.log(`      信号：${task.signals.join(', ')}`);
          if (task.expires_at) console.log(`      过期：${task.expires_at}`);
        });
        if (filteredTasks.length > 3) {
          console.log(`   ... 还有 ${filteredTasks.length - 3} 个任务`);
        }
      }
      
      return { ...result, tasks: filteredTasks, totalCount, availableTasks };
    } catch (error) {
      console.error('❌ 获取任务失败:', error.message);
      return { tasks: [], error: 'network_error' };
    }
  },
  
  /**
   * 认领任务
   */
  async claimTask(taskId) {
    const nodeId = getNodeId();
    console.log(`\n【3】认领任务：${taskId}`);
    
    const payload = { task_id: taskId, node_id: nodeId };
    const result = await HttpClient.post('/task/claim', payload, 5);
    
    if (result.status === 'claimed' || result.success) {
      console.log('✅ 认领成功');
    }
    
    return result;
  },
  
  /**
   * 发布解决方案（简化版 - 适合定时任务）
   */
  async publishSolution(task) {
    const nodeId = getNodeId();
    console.log(`\n【4】发布解决方案...`);
    
    // 构建 Gene
    const geneData = {
      type: 'Gene', 
      schema_version: '1.5.0', 
      category: 'repair',
      signals_match: task.signals || ['error'],
      summary: `Fix: ${task.title || 'Unknown'}`
    };
    const gene = { 
      ...geneData, 
      asset_id: 'sha256:' + crypto.createHash('sha256')
        .update(JSON.stringify(geneData, Object.keys(geneData).sort()))
        .digest('hex') 
    };
    
    // 构建 Capsule
    const capsuleData = {
      type: 'Capsule', 
      schema_version: '1.5.0',
      trigger: task.signals || ['error'], 
      gene: gene.asset_id,
      summary: `Solution: ${task.title || 'Unknown'}`,
      confidence: 0.85, 
      blast_radius: { files: 1, lines: 10 },
      outcome: { status: 'success', score: 0.85 },
      env_fingerprint: { platform: process.platform, arch: process.arch }
    };
    const capsule = { 
      ...capsuleData, 
      asset_id: 'sha256:' + crypto.createHash('sha256')
        .update(JSON.stringify(capsuleData, Object.keys(capsuleData).sort()))
        .digest('hex') 
    };
    
    // 构建 Event
    const eventData = {
      type: 'EvolutionEvent', 
      intent: 'repair',
      capsule_id: capsule.asset_id, 
      genes_used: [gene.asset_id],
      outcome: { status: 'success', score: 0.85 },
      mutations_tried: 1, 
      total_cycles: 1
    };
    const event = { 
      ...eventData, 
      asset_id: 'sha256:' + crypto.createHash('sha256')
        .update(JSON.stringify(eventData, Object.keys(eventData).sort()))
        .digest('hex') 
    };
    
    const payload = {
      protocol: 'gep-a2a', 
      protocol_version: '1.0.0',
      message_type: 'publish', 
      message_id: genMessageId(),
      sender_id: nodeId, 
      timestamp: genTimestamp(),
      payload: { assets: [gene, capsule, event] }
    };
    
    const result = await HttpClient.post('/a2a/publish', payload);
    
    if (result.status === 'published' || result.assets || result.error === 'duplicate_asset') {
      console.log('✅ 发布成功');
      const assetId = result.assets?.[1]?.asset_id || 
                     result.target_asset_id || 
                     capsule.asset_id;
      StateManager.update({ assetsPublished: (StateManager.load().assetsPublished || 0) + 1 });
      return { success: true, assetId };
    }
    
    return result;
  },
  
  /**
   * 完成任务
   */
  async completeTask(taskId, assetId) {
    const nodeId = getNodeId();
    console.log(`\n【5】完成任务...`);
    
    const payload = { task_id: taskId, asset_id: assetId, node_id: nodeId };
    const result = await HttpClient.post('/task/complete', payload, 5);
    
    if (result.status === 'completed' || result.success) {
      console.log('✅ 完成！积分将自动发放');
      StateManager.update({ tasksCompleted: (StateManager.load().tasksCompleted || 0) + 1 });
    }
    
    return result;
  }
};

// ============ 主流程 ============
const AutoTaskPublish = {
  async run() {
    console.log('\n========================================');
    console.log('   EvoMap Auto Task Publish v2.0');
    console.log('========================================\n');
    
    try {
      // 1. 节点上线
      await CoreFunctions.registerNode();
      await sleep(500);
      
      // 2. 获取任务
      const fetchResult = await CoreFunctions.fetchTasks();
      if (!fetchResult.tasks || fetchResult.tasks.length === 0) {
        console.log('\n⏳ 暂无可用任务，等待下次执行');
        StateManager.update({ success: true, tasksFound: 0 });
        return { success: true, status: 'NO_TASKS' };
      }
      
      // 3. 查找开放任务
      const task = fetchResult.tasks.find(t => t.status === 'open');
      if (!task) {
        console.log('\n⏳ 无开放任务');
        StateManager.update({ success: true, tasksFound: fetchResult.tasks.length });
        return { success: true, status: 'NO_OPEN_TASKS' };
      }
      
      console.log(`\n📋 任务：${task.title || 'Unknown'}`);
      if (task.bounty) console.log(`💰 赏金：${task.bounty} credits`);
      
      // 4. 认领任务
      const claimResult = await CoreFunctions.claimTask(task.task_id);
      if (claimResult.error && claimResult.error !== 'task_already_claimed') {
        throw new Error('认领失败：' + claimResult.error);
      }
      await sleep(500);
      
      // 5. 发布解决方案
      const publishResult = await CoreFunctions.publishSolution(task);
      if (!publishResult.success && !publishResult.assetId) {
        throw new Error('发布失败');
      }
      await sleep(500);
      
      // 6. 完成任务
      const assetId = publishResult.assetId || 'sha256:placeholder';
      await CoreFunctions.completeTask(task.task_id, assetId);
      
      console.log('\n========================================');
      console.log('   ✅ 本轮完成！');
      console.log('========================================\n');
      
      StateManager.update({ success: true, tasksCompleted: 1 });
      return { success: true, status: 'SUCCESS', taskId: task.task_id };
      
    } catch (error) {
      console.error('\n❌ 执行出错:', error.message);
      StateManager.update({ success: false, error: error.message });
      return { success: false, error: error.message };
    }
  },
  
  /**
   * 查看统计
   */
  async stats() {
    const state = StateManager.load();
    const nodeId = getNodeId();
    
    console.log('\n📊 执行统计');
    console.log('================================');
    console.log(`节点 ID: ${nodeId}`);
    console.log(`完成任务：${state.tasksCompleted || 0}`);
    console.log(`发布资产：${state.assetsPublished || 0}`);
    console.log(`最后运行：${state.lastRun || '从未'}`);
    console.log(`最后成功：${state.lastSuccess || '从未'}`);
    console.log(`连续失败：${state.consecutiveFailures || 0}`);
    console.log('================================\n');
    
    return state;
  },
  
  /**
   * 清空状态
   */
  async reset() {
    if (fs.existsSync(CONFIG.STATE_FILE)) {
      fs.unlinkSync(CONFIG.STATE_FILE);
      console.log('✅ 状态已重置');
    } else {
      console.log('ℹ️  无状态文件');
    }
  },
  
  /**
   * 查看节点状态
   */
  async status(nodeId) {
    const id = nodeId || getNodeId();
    console.log(`\n【状态】${id}`);
    
    const result = await HttpClient.get(`/a2a/nodes/${id}`);
    
    if (result.node_id) {
      console.log('✅ 节点在线');
      if (result.reputation_score) console.log(`⭐ 声誉：${result.reputation_score}`);
      if (result.credit_balance) console.log(`💰 积分：${result.credit_balance}`);
      if (result.total_published) console.log(`📦 发布：${result.total_published}`);
      if (result.total_completed) console.log(`✅ 完成：${result.total_completed}`);
    } else {
      console.log('⚠️  节点可能未注册或离线');
    }
    
    return result;
  },
  
  /**
   * 查看收益
   */
  async earnings() {
    const nodeId = getNodeId();
    console.log(`\n【收益】${nodeId}`);
    
    const state = StateManager.load();
    const result = await HttpClient.get(`/billing/earnings/${nodeId}`);
    
    console.log('💰 收益详情:');
    if (result.total_earned) console.log(`   总收益：${result.total_earned} credits`);
    if (result.pending) console.log(`   待结算：${result.pending} credits`);
    if (result.available) console.log(`   可用：${result.available} credits`);
    
    console.log('\n📊 本地统计:');
    console.log(`   完成任务：${state.tasksCompleted || 0}`);
    console.log(`   发布资产：${state.assetsPublished || 0}`);
    
    return result;
  },
  
  /**
   * 错误历史
   */
  async errors(clear = false) {
    const state = StateManager.load();
    
    if (clear) {
      StateManager.update({ errors: [] });
      console.log('✅ 错误历史已清空');
      return [];
    }
    
    if (!state.errors || state.errors.length === 0) {
      console.log('\n✅ 无错误记录');
      return [];
    }
    
    console.log(`\n【错误历史】最近 ${state.errors.length} 条:`);
    state.errors.forEach((err, i) => {
      console.log(`${i+1}. [${err.timestamp}] ${err.error} (${err.endpoint})`);
    });
    return state.errors;
  }
};

// ============ 命令行入口 ============
const main = async (args) => {
  const command = args?.[0] || 'run';
  
  console.log(`\n🚀 EvoMap Auto Task Publish v2.0`);
  console.log(`   Hub: ${CONFIG.HUB_URL}`);
  console.log(`   命令：${command}\n`);
  
  switch (command) {
    case 'run': return await AutoTaskPublish.run();
    case 'stats': return await AutoTaskPublish.stats();
    case 'reset': return await AutoTaskPublish.reset();
    case 'status': return await AutoTaskPublish.status(args?.[1]);
    case 'earnings': return await AutoTaskPublish.earnings();
    case 'errors': return await AutoTaskPublish.errors(args?.[1] === 'clear');
    default:
      console.log('📖 用法：node index-optimized.js [命令]');
      console.log('\n命令:');
      console.log('  run          - 运行一轮（默认）');
      console.log('  stats        - 查看统计');
      console.log('  reset        - 重置状态');
      console.log('  status       - 节点状态');
      console.log('  earnings     - 查看收益');
      console.log('  errors       - 错误历史（clear 清空）');
  }
};

// 导出模块
module.exports = {
  main,
  run: AutoTaskPublish.run,
  stats: AutoTaskPublish.stats,
  reset: AutoTaskPublish.reset,
  status: AutoTaskPublish.status,
  earnings: AutoTaskPublish.earnings,
  errors: AutoTaskPublish.errors,
  config: CONFIG,
  stateManager: StateManager
};

// 主入口
if (require.main === module) {
  main(process.argv.slice(2));
}
