import asyncio
from typing import Dict, List, Any
from openagents.agents.worker_agent import WorkerAgent, on_event
from openagents.models.event import Event
from openagents.models.event_context import EventContext
from openagents.models.agent_config import AgentConfig
from openagents.utils.password_utils import hash_password

class RefinementAgent(WorkerAgent):
    """Agent that checks and refines research ideas with iterative optimization."""

    default_agent_id = "refinement_agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.idea_buffer: Dict[str, Dict[str, Any]] = {}
        self.current_round: int = 0
        self.max_rounds: int = 2

    @on_event("idea.check")
    async def on_check_request(self, context: EventContext):
        """Handle request to check ideas for methodology and experimental setup issues."""
        ideas = context.incoming_event.payload.get("ideas", [])
        round_num = context.incoming_event.payload.get("round", 1)
        self.current_round = round_num
        
        checked_ideas = []
        needs_method_improvement = []
        needs_experiment_improvement = []
        
        for idea in ideas:
            checked_idea = await self.check_idea(idea, round_num)
            checked_ideas.append(checked_idea)
            
            if checked_idea.get("needs_method_improvement", False):
                needs_method_improvement.append(checked_idea)
            
            if checked_idea.get("needs_experiment_improvement", False):
                needs_experiment_improvement.append(checked_idea)
        
        all_passed = len(needs_method_improvement) == 0 and len(needs_experiment_improvement) == 0
        
        formatted_text = f"🔍 完善Agent检查结果（第{int(round_num)}轮）：\n\n"
        for i, checked_idea in enumerate(checked_ideas, 1):
            title = checked_idea.get("title", f"创意{i}")
            status = "✅ 通过" if not (checked_idea.get("needs_method_improvement") or checked_idea.get("needs_experiment_improvement")) else "⚠️ 需要改进"
            formatted_text += f"{status} {title}\n"
            if checked_idea.get("method_feedback"):
                formatted_text += f"   方法反馈：{checked_idea['method_feedback']}\n"
            if checked_idea.get("experiment_feedback"):
                formatted_text += f"   实验反馈：{checked_idea['experiment_feedback']}\n"
            formatted_text += "\n"
        
        await self.post_to_channel("discussion", formatted_text)
        
        await self.send_event(Event(
            event_name="idea.check.result",
            destination_id="leader",
            payload={
                "round": round_num,
                "all_passed": all_passed,
                "ideas": checked_ideas,
                "needs_method_improvement": needs_method_improvement,
                "needs_experiment_improvement": needs_experiment_improvement,
                "count": len(checked_ideas)
            }
        ))

    async def check_idea(self, idea: Dict[str, Any], round_num: int) -> Dict[str, Any]:
        """Check a single idea for methodology and experimental setup issues."""
        
        checked_idea = idea.copy()
        
        methodology = idea.get("methodology", "")
        experimental_setup = idea.get("experimental_setup", "")
        title = idea.get("title", "")
        
        method_feedback = ""
        experiment_feedback = ""
        needs_method_improvement = False
        needs_experiment_improvement = False
        
        if not methodology or len(methodology) < 50:
            method_feedback = "方法论描述过于简略，需要更详细的研究方法说明"
            needs_method_improvement = True
        else:
            method_issues = []
            
            if "步骤" not in methodology and "流程" not in methodology and "过程" not in methodology:
                method_issues.append("缺乏具体的实施步骤")
            
            if "数据" in title or "数据集" in title:
                if "预处理" not in methodology and "清洗" not in methodology:
                    method_issues.append("数据预处理流程不明确")
                if "标注" in title and "标注" not in methodology:
                    method_issues.append("数据标注方法未说明")
            
            if "模型" in title or "网络" in title or "算法" in title:
                if "架构" not in methodology and "结构" not in methodology:
                    method_issues.append("模型架构描述不清晰")
                if "参数" not in methodology and "超参数" not in methodology:
                    method_issues.append("模型参数设置未说明")
                if "训练" in title and "训练" not in methodology:
                    method_issues.append("训练策略不明确")
            
            if "联邦" in title:
                if "通信" not in methodology and "聚合" not in methodology:
                    method_issues.append("联邦学习的通信和聚合机制未说明")
                if "隐私" in title and "加密" not in methodology and "差分" not in methodology:
                    method_issues.append("隐私保护机制未详细说明")
            
            if "多模态" in title or "跨" in title:
                if "融合" not in methodology and "对齐" not in methodology:
                    method_issues.append("多模态数据融合或对齐方法未说明")
            
            if "物理" in title or "合成" in title:
                if "仿真" not in methodology and "模拟" not in methodology:
                    method_issues.append("物理仿真或模拟方法未说明")
            
            if "3D" in title or "重建" in title:
                if "渲染" not in methodology and "投影" not in methodology:
                    method_issues.append("3D重建或渲染方法未说明")
            
            if method_issues:
                method_feedback = "；".join(method_issues)
                needs_method_improvement = True
            else:
                method_feedback = "方法论描述较为完整"
        
        if not experimental_setup or len(experimental_setup) < 50:
            experiment_feedback = "实验设置描述过于简略，需要更详细的实验配置说明"
            needs_experiment_improvement = True
        else:
            experiment_issues = []
            
            if "数据集" not in experimental_setup and "数据" not in experimental_setup:
                experiment_issues.append("缺乏数据集信息")
            
            if "设备" not in experimental_setup and "硬件" not in experimental_setup:
                experiment_issues.append("缺乏硬件设备配置")
            
            if "评估" not in experimental_setup and "指标" not in experimental_setup:
                experiment_issues.append("缺乏评估指标")
            
            if "对比" not in experimental_setup and "基线" not in experimental_setup:
                experiment_issues.append("缺乏对比实验或基线方法")
            
            if "消融" not in experimental_setup and "ablation" not in experimental_setup:
                experiment_issues.append("建议增加消融实验")
            
            if "参数" not in experimental_setup and "超参数" not in experimental_setup:
                experiment_issues.append("参数设置未详细说明")
            
            if "训练" in title and "训练" not in experimental_setup:
                experiment_issues.append("训练配置不明确")
            
            if "联邦" in title and "节点" not in experimental_setup:
                experiment_issues.append("联邦节点配置未说明")
            
            if "多模态" in title and "采集" not in experimental_setup:
                experiment_issues.append("多模态数据采集配置未说明")
            
            if experiment_issues:
                experiment_feedback = "；".join(experiment_issues)
                needs_experiment_improvement = True
            else:
                experiment_feedback = "实验设置描述较为完整"
        
        checked_idea["method_feedback"] = method_feedback
        checked_idea["experiment_feedback"] = experiment_feedback
        checked_idea["needs_method_improvement"] = needs_method_improvement
        checked_idea["needs_experiment_improvement"] = needs_experiment_improvement
        checked_idea["check_round"] = round_num
        
        await asyncio.sleep(0.1)
        
        return checked_idea

    @on_event("research.ideas.clear")
    async def on_clear_buffer(self, context: EventContext):
        """Clear the idea and review buffers."""
        self.idea_buffer.clear()
        self.current_round = 0
        
        await self.send_event(Event(
            event_name="research.ideas.cleared",
            destination_id="leader",
            payload={"status": "buffers_cleared"}
        ))


if __name__ == "__main__":
    agent_config = AgentConfig(
        instruction="你是完善Agent。你的任务是检查研究创意的方法论和实验设置是否充分，并提供改进建议。如果发现不足，将需要改进的创意交由相应的专家进行修改，直到优化完成（最多3轮）。",
        model_name="qwen3-max-preview",
        provider="openai-compatible",
        max_iterations=10
    )
    agent = RefinementAgent(agent_config=agent_config)
    agent.start(network_host="localhost", network_port=8709, password_hash=hash_password("openagents"))
    agent.wait_for_stop()