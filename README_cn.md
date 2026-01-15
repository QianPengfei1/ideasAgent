# 研究创意生成网络

一个使用OpenAgents框架生成和评估研究创意的多智能体系统。该系统通过协作工作流协调专门的智能体来生成高质量的研究提案。

## 概述

研究创意生成网络采用协作式多智能体方法来：
- 从多个角度生成多样化的研究创意
- 基于技术可行性和影响力评估创意
- 根据反馈优化和整合创意
- 对创意进行评分和排名以供最终选择

## 架构

### 智能体类型

1. **Leader Agent（领导者智能体）** (`leader_agent.yaml`)
   - 协调整个创意生成过程
   - 将任务委托给其他智能体
   - 控制工作流进展
   - 向用户展示最终结果

2. **Generator Agents（生成器智能体）**（3个专门智能体）
   - **Domain Agent（领域智能体）**：深入研究给定的研究领域
   - **Method Agent（方法智能体）**：改进研究创意的方法论
   - **Application Agent（应用智能体/实验智能体）**：改进研究创意的实验设置

3. **Refinement Agent（优化智能体）** (`refinement_agent.py`)
   - 检查创意的方法论和实验设置问题
   - 提供具体的改进反馈
   - 与方法智能体和应用智能体协调进行迭代优化
   - 支持最多2轮优化

4. **Evaluation Agent（评估智能体）** (`evaluation_agent.yaml`)
   - 对研究创意进行多标准评估
   - 基于5个维度评分：
     * 技术可行性（权重25%）
     * 影响力（权重30%）
     * 新颖性（权重20%）
     * 相关性（权重15%）
     * 清晰度（权重10%）
   - 对创意进行排名和选择Top-K
   - 提供详细的评估报告，包括优势、劣势和建议

## 工作流程

系统遵循6步迭代工作流程：

1. **Domain Agent生成初始创意**
   - 用户提供研究领域或主题
   - Domain Agent从领域角度生成5个研究创意
   - 创意包括基本问题陈述、核心思想和初始方法论/实验设置

2. **Method Agent改进方法论**
   - Method Agent接收5个创意
   - 使用详细的研究方法改进每个创意的方法论部分
   - 将增强的创意返回给Leader Agent

3. **Application Agent（实验智能体）改进实验设置**
   - Application Agent接收5个具有改进方法论的创意
   - 使用具体实施细节增强实验设置部分
   - 将优化的创意返回给Leader Agent

4. **Refinement Agent检查并迭代改进（最多2轮）**
   - Refinement Agent检查所有5个创意的方法论和实验设置问题
   - 为每个创意提供具体的、领域特定的反馈
   - 如果发现问题，发送回Method Agent或Application Agent进行改进
   - 过程重复直到所有创意通过检查或达到最大2轮

5. **Evaluation Agent对创意进行评分和排名**
   - Evaluation Agent从5个维度评估所有创意：
     * 技术可行性（1-10分，权重25%）
     * 影响力（1-10分，权重30%）
     * 新颖性（1-10分，权重20%）
     * 相关性（1-10分，权重15%）
     * 清晰度（1-10分，权重10%）
   - 计算加权总分并排名创意
   - 返回Top-K排名创意及详细评估

6. **Leader Agent展示最终结果**
   - Leader Agent格式化并向用户展示排名的创意
   - 包括详细的方法论、实验设置和评估分数
   - 显示每个创意的优势、劣势和建议

## 安装

### 前置要求

- Python 3.8+
- 已安装OpenAgents框架
- 可访问OpenAgents服务器的网络连接

### 设置

1. 克隆或导航到网络目录：
```bash
cd demos/09_research_ideas_network
```

2. 确保所有智能体文件都已就位：
```
demos/09_research_ideas_network/
├── network.yaml
├── agents/
│   ├── leader_agent.yaml
│   ├── domain_agent.yaml
│   ├── method_agent.yaml
│   ├── application_agent.yaml
│   ├── evaluation_agent.yaml
│   └── refinement_agent.py
├── start_all.sh
└── stop_all.sh
```

## 使用

### 启动网络

启动网络服务器：

```bash
openagents network start 09_research_ideas_network/network.yaml
```

网络将在以下地址启动：
- HTTP: `http://localhost:8709`
- gRPC: `localhost:8609`

### 启动智能体

#### 快速启动（推荐）

使用提供的启动脚本一次性启动所有智能体：

```bash
./start_all.sh
```

这将按正确顺序启动所有核心智能体：
1. 网络服务器
2. Leader Agent
3. Domain Agent
4. Method Agent
5. Application Agent（实验智能体）
6. Evaluation Agent
7. Refinement Agent

#### 手动启动（用于调试）

在单独的终端中启动每个智能体：

```bash
# Leader Agent
openagents agent start 09_research_ideas_network/agents/leader_agent.yaml

# Domain Agent
openagents agent start 09_research_ideas_network/agents/domain_agent.yaml

# Method Agent
openagents agent start 09_research_ideas_network/agents/method_agent.yaml

# Application Agent
openagents agent start 09_research_ideas_network/agents/application_agent.yaml

# Evaluation Agent
openagents agent start 09_research_ideas_network/agents/evaluation_agent.yaml
```

#### 启动基于Python的智能体

启动Refinement Agent：

```bash
python 09_research_ideas_network/agents/refinement_agent.py
```

#### 停止所有智能体

使用提供的停止脚本：

```bash
./stop_all.sh
```

### 使用系统

一旦所有智能体都连接成功，与Leader Agent交互以生成研究创意：

1. 向Leader Agent发送直接消息，提供您的研究领域/主题
2. 系统将自动：
   - 从领域角度生成5个初始创意
   - 使用Method Agent改进方法论
   - 使用Application Agent增强实验设置
   - 通过迭代检查优化创意（最多2轮）
   - 从5个维度评估所有创意并排名
3. 接收Top-K研究创意及详细评估

## 频道推送

- 所有智能体都会向 `discussion` 频道推送进度（与 Refinement Agent 一致）。
- 频道消息工具为 `send_channel_message(channel, content)`（注意参数名是 `channel`，不是 `channel_id`）。

## 工具参数格式

- 工具调用参数必须是严格 JSON，且必须单行输出（字符串中禁止原始换行，使用 `\n`）。
- 字符串中如包含双引号，必须转义为 `\"`。
- 工具参数中禁止包含 `reason` 等额外字段；调用 `finish` 时使用 `{}`。

示例交互：
```
用户：我需要步态识别研究创意
Leader：我将协调步态识别研究创意的生成。让我将任务委托给我们的专门智能体...
[... 智能体顺序工作 ...]
Leader：以下是步态识别的前5个研究创意：
1. [创意1，包含分数和详细信息]
2. [创意2，包含分数和详细信息]
...
```

## 配置

### 网络配置

编辑`network.yaml`以自定义：
- 网络端口（HTTP: 8709, gRPC: 8609）
- 智能体组和权限

### 智能体配置

编辑各个智能体YAML文件以自定义：
- 模型选择
- 指令和行为
- 最大迭代次数
- 响应模式

### 评估配置

编辑`agents/evaluation_agent.yaml`中的评估智能体配置以调整：
- 评估维度（technical_feasibility, impact, novelty, relevance, clarity）
- 每个维度的权重
- 分数范围（1-10）
- Top-K选择标准

## 数据结构

### 研究创意格式

```json
{
  "idea_id": "唯一标识符",
  "title": "研究创意标题",
  "problem": "问题陈述",
  "core_idea": "核心创新",
  "why_interesting": "为什么有趣",
  "methodology": "详细的研究方法论",
  "experimental_setup": "实验设计和设置",
  "challenges": "潜在挑战"
}
```

### 评估结果格式

```json
{
  "idea_id": "唯一ID",
  "idea_title": "创意标题",
  "scores": {
    "technical_feasibility": 8.5,
    "impact": 9.0,
    "novelty": 7.5,
    "relevance": 8.0,
    "clarity": 9.0
  },
  "total_score": 8.4,
  "evaluation": {
    "technical_feasibility": {
      "score": 8.5,
      "reasoning": "技术可行性分数的详细推理"
    },
    "impact": {
      "score": 9.0,
      "reasoning": "影响力分数的详细推理"
    },
    "novelty": {
      "score": 7.5,
      "reasoning": "新颖性分数的详细推理"
    },
    "relevance": {
      "score": 8.0,
      "reasoning": "相关性分数的详细推理"
    },
    "clarity": {
      "score": 9.0,
      "reasoning": "清晰度分数的详细推理"
    }
  },
  "strengths": ["优秀的影响力", "良好的技术可行性"],
  "weaknesses": ["中等的新颖性"],
  "suggestions": ["考虑融入更多创新元素"]
}
```

## 故障排除

### 智能体无法连接

- 验证网络是否正在运行：`openagents network status`
- 检查智能体配置中的网络URL和端口
- 确保网络和智能体之间的密码匹配

### 创意未生成

- 验证所有生成器智能体都已连接
- 检查Leader Agent日志中的委托错误
- 确保智能体组具有正确的权限

### 评估不工作

- 验证Evaluation Agent是否正在运行：检查智能体启动日志
- 检查evaluation_agent.yaml配置
- 确保事件名称匹配：`idea.evaluate`和`idea.evaluated`

## 开发

### 添加新的生成器智能体

1. 在`agents/`目录中创建新的YAML文件
2. 遵循现有生成器智能体的结构
3. 将智能体添加到`network.yaml`中的适当智能体组
4. 更新Leader Agent工作流程以包含新智能体

### 修改评估标准

编辑`agents/evaluation_agent.yaml`中的评估标准以调整：
- 评估维度及其权重
- 分数范围和阈值
- 评估提示和指令

当前评估使用5个维度：
- 技术可行性（权重25%）
- 影响力（权重30%）
- 新颖性（权重20%）
- 相关性（权重15%）
- 清晰度（权重10%）

### 自定义工作流程

修改`agents/leader_agent.yaml`中的工作流程以更改：
- 智能体序列和协调
- 优化轮数
- Top-K选择标准
- 事件名称和负载

## 许可证

本项目是OpenAgents框架的一部分。

## 贡献

欢迎贡献！请向OpenAgents仓库提交问题和拉取请求。
