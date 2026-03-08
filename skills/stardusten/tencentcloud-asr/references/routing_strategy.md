# 音频路由与大文件处理策略

> **何时必须阅读本文件**：
> - 输入是公网 `http://` / `https://` URL
> - 音频超过 60 秒
> - 文件可能超过 3MB / 100MB
> - 需要在 `flash_recognize.py` 与 `file_recognize.py` 之间做选择
> - 需要判断当前脚本是否支持 body 上传

## 核心结论

1. **公网 URL 且音频已合规时，优先 URL 路径**
   - “已合规”指：`sample_rate == 16000`、`channels == 1`
   - 这样可以避免本地转码、切片和重新上传
2. **本地文件或不合规 URL，先转成本地标准 WAV**
   - 标准格式固定为：`16kHz`、单声道、`pcm_s16le`、`.wav`
3. **本地标准 WAV 的默认大文件策略是切片后逐片走 Flash**
   - 只有明确命中异步 / URL / 高级结果格式需求时，才走 `file_recognize.py`

## 硬阈值

- `SHORT_MAX_SECONDS = 60`
- `SENTENCE_MAX_BYTES = 3145728`（3MB）
- `FLASH_MAX_SECONDS = 7200`（2 小时）
- `FLASH_MAX_BYTES = 104857600`（100MB）
- `FILE_ASYNC_MAX_SECONDS = 18000`（5 小时）
- `FILE_BODY_MAX_BYTES = 5242880`（5MB）
- `SEGMENT_SECONDS = 1800`（30 分钟）

## 第 1 部分：先探测元数据

统一先执行：

```bash
python3 <SKILL_DIR>/scripts/inspect_audio.py "<AUDIO_INPUT>"
```

如果返回 `requires_ffprobe_or_ffmpeg`，先执行：

```bash
python3 <SKILL_DIR>/scripts/ensure_ffmpeg.py --execute
```

然后重新探测。

**例外：公网 URL 的异步快速路径**

如果同时满足：

- 输入本来就是公网 `http://` / `https://` URL
- `inspect_audio.py` 失败的主要原因是本机缺少 `ffprobe`，或远端 URL 探测超时
- 你当前本来就倾向于走异步 URL 识别

那么不要被“本地探测失败”卡住。可以直接尝试：

```bash
python3 <SKILL_DIR>/scripts/file_recognize.py "<PUBLIC_URL>"
```

只有当它真实返回格式错误、时长超限、URL 不可下载或其他 API 错误时，才转入本地下载 / 转码 / 切片链。

## 第 2 部分：公网 URL 的判断链

### 2.1 什么时候认定为“可直接走 URL”

必须同时满足：

- 输入本身是公网 `http://` / `https://` URL
- `inspect_audio.py` 能成功拿到元数据
- `sample_rate == 16000`
- `channels == 1`

只要以上四项有任意一项不满足，就不要直接走 URL 路径，转到“本地处理链”。

### 2.2 公网 URL 的脚本选择

如果是“可直接走 URL”的公网音频：

1. 如果同时满足：
   - `duration_seconds <= 60`
   - 且能确认文件满足一句话识别大小上限
   那么使用：
   ```bash
   python3 <SKILL_DIR>/scripts/main.py "<PUBLIC_URL>"
   ```

2. 如果：
   - `60 < duration_seconds <= 18000`
   那么默认优先：
   ```bash
   python3 <SKILL_DIR>/scripts/file_recognize.py "<PUBLIC_URL>"
   ```

3. 如果：
   - `duration_seconds > 18000`
   那么 `file_recognize.py` 也不适用，转到“本地处理链”

### 2.3 公网 URL 何时不要优先走 URL

命中以下任一条件，就不要直接走 URL 路径：

- `sample_rate != 16000`
- `channels != 1`
- 用户明确要求**同步**返回且你确认本地处理更合适
- `duration_seconds > 5h`
- `inspect_audio.py` 对 URL 探测失败

以上情况统一转到“本地处理链”。

### 2.4 公网 URL 的操作禁忌

对于已经满足“优先 URL 路径”条件的公网音频，默认不要做这些事：

- 不要先下载到本地再判断
- 不要先尝试安装 `ffprobe` 只为了拿更漂亮的元数据
- 不要先手动 `curl`、`file`、`grep` 做临时探测
- 不要先读脚本源码确认凭证读取逻辑
- 不要先检查 Python 依赖是否已安装

正确做法是：拿到凭证后，直接调用目标脚本；只有在目标脚本真实失败时，才进入下一层诊断。

## 第 3 部分：本地处理链

### 3.1 先规范化

如果满足以下任一条件，就必须先转码，生成本地标准 WAV：

- 输入本来就是本地文件
- 输入是 URL 但不满足“可直接走 URL”的四个条件
- `sample_rate != 16000`
- `channels != 1`
- `container_format != "wav"`

统一转码命令：

```bash
ffmpeg -y -i "<INPUT_AUDIO>" -ac 1 -ar 16000 -c:a pcm_s16le "<NORMALIZED_WAV>"
```

转码后：

- `WORKING_AUDIO_FILE = NORMALIZED_WAV`

如果无需转码但已经是本地文件：

- `WORKING_AUDIO_FILE = LOCAL_AUDIO_FILE`

### 3.2 本地文件脚本选择

对 `WORKING_AUDIO_FILE` 同时读取：

- `duration_seconds`
- `file_size_bytes`

然后按下面顺序判断：

1. 如果同时满足：
   - `duration_seconds <= 60`
   - `file_size_bytes <= 3145728`
   使用：
   ```bash
   python3 <SKILL_DIR>/scripts/main.py "<WORKING_AUDIO_FILE>"
   ```

2. 如果同时满足：
   - `duration_seconds <= 7200`
   - `file_size_bytes <= 104857600`
   使用：
   ```bash
   python3 <SKILL_DIR>/scripts/flash_recognize.py "<WORKING_AUDIO_FILE>"
   ```

3. 如果命中以下任一条件：
   - `duration_seconds > 7200`
   - `file_size_bytes > 104857600`
   那么必须先切片，再逐片使用 `flash_recognize.py`

### 3.3 固定切片方案

切片命令：

```bash
ffmpeg -y -i "<WORKING_AUDIO_FILE>" -f segment -segment_time 1800 -c:a pcm_s16le -ar 16000 -ac 1 "<SEGMENT_DIR>/part_%03d.wav"
```

切片后对每一个分片都必须确认：

- `duration_seconds <= 7200`
- `file_size_bytes <= 104857600`

然后逐片执行：

```bash
python3 <SKILL_DIR>/scripts/flash_recognize.py "<SEGMENT_FILE>"
```

最后按文件名顺序拼接文本结果。

## 第 4 部分：什么时候才允许 `file_recognize.py`

除“公网 URL 且已合规”的优先路径外，只有命中以下任一条件，才允许主动选择 `file_recognize.py`：

1. 用户明确要求异步任务 / `TaskId` / `--no-poll`
2. 用户明确要求 `--res-text-format 4` 或 `--res-text-format 5`
3. 输入是公网 URL，且符合 `file_recognize.py` 的 URL 条件
4. 本地磁盘空间不足，无法完成规范化或切片

不要把 `file_recognize.py` 当成本地大文件默认方案。

## 第 5 部分：脚本上传方式校验

当前脚本对“通过 body 传音频内容”的支持如下：

### `main.py`

- 本地文件：支持
- URL：支持
- 实现方式：
  - 本地文件走 `SourceType=1 + Data + DataLen`
  - URL 走 `SourceType=0 + Url`

### `flash_recognize.py`

- 本地文件：支持
- URL：脚本输入支持，但会先下载，再用请求 `Body` 上传原始字节
- 实现方式：
  - 最终总是 `POST Body` 传音频二进制

### `file_recognize.py`

- 本地文件：仅 `<= 5MB` 支持
- URL：支持
- 实现方式：
  - 本地小文件走 `SourceType=1 + Data + DataLen`
  - 公网 URL 走 `SourceType=0 + Url`

## 第 6 部分：为什么不默认要求 COS

腾讯云官方对 `CreateRecTask` 的要求是“公网可下载 URL”，并不是“必须 COS”。

因此：

- 如果用户已经给了公网可下载 URL，不要默认要求 COS
- 如果用户给的是本地大文件，也不要先让用户配 COS
- 只有在你最终确定必须走异步 URL 接口、且用户又没有可用公网 URL 时，才可以把“需要公网可下载链接”告诉用户

## 第 7 部分：凭证注入的最短路径

为了减少“写 profile / source / 子进程没继承环境变量”这种弯路，默认遵循：

1. **单次任务**：把密钥直接注入当前执行命令或当前子进程环境。
2. **只有明确需要持久化时**：才写 `~/.zshrc`、`~/.bashrc` 或对应系统配置。

不要为了完成当前一次识别任务，先去：

- 写 `~/.bashrc`
- 写 `~/.zshrc`
- 执行 `source ~/.bashrc`
- 执行 `source ~/.zshrc`

先把识别任务跑通，再考虑是否需要持久化。
