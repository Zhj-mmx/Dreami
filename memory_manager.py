import json
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self, max_history_length=10, save_to_file=True):
        """
        初始化对话记忆管理器
        
        Args:
            max_history_length: 最大对话轮数（每轮包含用户和AI的对话）
            save_to_file: 是否保存到文件
        """
        self.max_history_length = max_history_length
        self.save_to_file = save_to_file
        self.memory_file = "conversation_memory.json"

        # 对话历史结构：包含系统提示和对话历史
        self.conversation_history = [
            {"role":"system","content":"你是一个友好的ai助手，乐于助人且热情"}
        ]

        # 加载之前的记忆（如果存在）
        self._load_memory()

    def add_exchange(self, user_input, ai_response):
        """添加一轮对话交换"""
        # 添加用户输入
        self.conversation_history.append({
            "role":"user",
            "content":user_input,
            "timestamp": datetime.now().isoformat()
        })

        # 添加AI回复
        self.conversation_history.append({
            "role":"assistant",
            "content":ai_response,
            "timestamp": datetime.now().isoformat()
        })

        # 保持历史长度不超过限制（注意保留系统提示）
        self._trim_history()

        # 保存记忆
        if self.save_to_file:
            self._save_summary()

    def get_context(self, max_message=None):
        """获取对话上下文（用于API调用）"""
        if max_message:
             # 返回最新的若干条消息，但总是包含系统提示
             messages = [self.conversation_history[0]]
             start_idx = max(1, len(self.conversation_history) - max_message * 2)
             messages.extend(self.conversation_history[start_idx:])
             return messages
        else:
            return self.conversation_history.copy()
    
    def clear_history(self):
        """清除对话历史（保留系统提示）"""
        self.conversation_history = [self.conversation_history[0]]
        if self.save_to_file:
            self._save_memory()

    def get_memory(self):
        """获取对话摘要（简易版）"""
        user_messages = [msg["content"] for msg in self.conversation_history if msg ["role"] == "user"]
        if len(user_messages) > 3:
            return f"最近讨论了：{user_messages[-3]}等话题"
        elif user_messages:
            return f"讨论了:{','.join(user_messages[-2:])}"
        else: 
            return "对话刚开始"

    def _trim_history(self):
        """修剪历史，保持长度不超过限制"""        
        # 计算最大条数：系统提示 + max_history_length * 2（每轮2条）
        max_entries = 1 + (self.max_history_length * 2)
        if len(self.conversation_history) > max_entries:
            # 保留系统提示和最近的对话
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-max_entries+1:]

    def _save_memory(self):
        """保存记忆到文件"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆失败:{e}")

    def _load_memory(self):
        """从文件加载记忆"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                    # 确保有系统提示
                    if loaded_history and loaded_history[0]["role"] == "system":
                        self.conversation_history = loaded_history
                    print(f"已加载之前的对话记忆,共{len(self.conversation_history)-1}条对话记录")
            except Exception as e:
                print(f"加载记忆失败:{e}")

    def __str__(self):
        """字符串表示"""            
        user_count = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        return f"对话记忆管理器:{user_count}轮对话记录"
    

    







 