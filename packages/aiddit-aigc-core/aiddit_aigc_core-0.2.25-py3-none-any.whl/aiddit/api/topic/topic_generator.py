from tenacity import retry, stop_after_attempt, wait_fixed

from aiddit.api.xhs_api import _get_xhs_account_info, _get_xhs_account_note_list, _get_note_detail_by_id
import aiddit.api.topic.prompt as prompt
import aiddit.model.google_genai as google_genai
import aiddit.utils as utils
from aiddit.model.google_genai import GenaiConversationMessage, GenaiMessagePart, MessageType
import os
import aiddit.api.history_note as history_note


def reference_note_available(xhs_user_id: str, reference_note_id: str):
    account_info = _get_xhs_account_info(xhs_user_id)
    account_history_note_path = _get_xhs_account_note_list(xhs_user_id)

    model = google_genai.MODEL_GEMINI_2_5_FLASH

    reference_note = _get_note_detail_by_id(reference_note_id)

    history_notes = utils.load_from_json_dir(account_history_note_path)

    history_messages = []

    history_messages.extend(history_note.build_history_note_messages(history_notes))

    # 参考帖子
    if reference_note.get("content_type") == "video" and reference_note.get("video", {}).get("video_url") is not None:
        reference_note_medias = [reference_note.get("video", {}).get("video_url")]
    else:
        reference_note_medias = [utils.oss_resize_image(i) for i in
                                 utils.remove_duplicates(reference_note.get("images"))]
    reference_note_prompt = prompt.REFERENCE_NOTE_PROVIDER_PROMPT.format(
        title=reference_note.get("title"),
        body_text=reference_note.get("body_text"),
        image_count=len(reference_note_medias)
    )
    reference_note_conversation_user_message = google_genai.GenaiConversationMessage.text_and_images(
        reference_note_prompt, reference_note_medias)
    history_messages.append(reference_note_conversation_user_message)

    # 获取当前文件的目录
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    print("current_file_dir ---", current_file_dir)
    # 专家知识
    expert_knowledge_path = os.path.join(current_file_dir, "../expert/topic_theory_expert.txt")
    print("expert_knowledge_path ---", expert_knowledge_path)

    if os.path.exists(expert_knowledge_path):
        expert_knowledge_conversation_user_message = google_genai.GenaiConversationMessage.text_and_images(
            f"小红书内容创作的理论基石：基于特定账号人设与参考帖子的选题策略。从中你可以学习 了解小红书内容创作的理论基石，基于特定账号人设与参考帖子的选题策略。",
            expert_knowledge_path)
        history_messages.append(expert_knowledge_conversation_user_message)
    else:
        print("expert_knowledge_path not exist , skip expert knowledge")

    # 参考帖子是否能产生选题
    reference_available_prompt = prompt.REFERENCE_NOTE_AVAILABLE_PROMPT.format(
        account_name=account_info.get("account_name"),
        account_description=account_info.get("description"), )
    reference_available_conversation_user_message = GenaiConversationMessage.one("user",
                                                                                 reference_available_prompt)

    system_prompt_count = google_genai.google_genai_client.models.count_tokens(model=model,contents=prompt.SYSTEM_INSTRUCTION_PROMPT)
    print("system_prompt_count ---", system_prompt_count)

    script_ans_conversation_model_message = google_genai.google_genai_output_images_and_text(
        reference_available_conversation_user_message,
        model=model,
        history_messages=history_messages,
        system_instruction_prompt=prompt.SYSTEM_INSTRUCTION_PROMPT)
    ans_content = script_ans_conversation_model_message.content[0].value

    return ans_content, [script_ans_conversation_model_message.usage_metadata]


def topic_generate_by_persona(topic_persona, reference_note_id):
    model = google_genai.MODEL_GEMINI_2_5_PRO_EXPT_0325
    history_messages = []
    reference_note = _get_note_detail_by_id(reference_note_id)
    # 参考帖子
    if reference_note.get("content_type") == "video" and reference_note.get("video", {}).get("video_url") is not None:
        reference_note_medias = [reference_note.get("video", {}).get("video_url")]
    else:
        reference_note_medias = [utils.oss_resize_image(i) for i in
                                 utils.remove_duplicates(reference_note.get("images"))]
    reference_note_prompt = prompt.REFERENCE_NOTE_PROVIDER_PROMPT.format(
        title=reference_note.get("title"),
        body_text=reference_note.get("body_text"),
        image_count=len(reference_note_medias)
    )
    reference_note_conversation_user_message = google_genai.GenaiConversationMessage.text_and_images(
        reference_note_prompt, reference_note_medias)
    history_messages.append(reference_note_conversation_user_message)

    topic_generate_by_persona_and_reference_note_prompt = prompt.TOPIC_GENERATE_BY_PERSONA_AND_REFERENCE_NOTE_PROMPT.format(
        persona_topic=topic_persona,
    )
    topic_generate_conversation_user_message = GenaiConversationMessage.one("user", topic_generate_by_persona_and_reference_note_prompt)


    script_ans_conversation_model_message = google_genai.google_genai_output_images_and_text(
        topic_generate_conversation_user_message,
        model=model,
        history_messages=history_messages,
        system_instruction_prompt=prompt.SYSTEM_INSTRUCTION_PROMPT)
    ans_content = script_ans_conversation_model_message.content[0].value

    return ans_content, [script_ans_conversation_model_message.usage_metadata]


if __name__ == "__main__":
    persona = """作为一名小红书人设构建专家，我对账号“胖胖胖胖总”进行了深度分析。以下是基于该账号历史帖子的客观总结：

### 账号核心信息
*   **账号名：** 胖胖胖胖总
*   **账号描述：** 🍬普本->猎头公司合伙人->资深HRD->集齐京沪深杭的职场博主；🍬曾在985大学授课|上过《三联生活周刊》|行业专家；📮合作：ppppzong@qq.com

### 账号内容分析

#### 1. 账号内容的品类
*   **核心品类：**
    *   **职场观察与解读：** 约占60%。涵盖大厂文化、职场PUA、裁员、内卷、升职路径、职业发展等。
    *   **社会热点深度剖析：** 约占30%。以时下热门“吃瓜”事件为载体，剖析其背后的社会阶层、人性、教育、婚恋等深层逻辑。
    *   **个人成长与认知升级：** 约占10%。通过对职场与社会现象的观察，提炼出关于个人成长、认知纠错和心态调整的建议。
*   **一句话总结账号的核心内容品类和创作方向：** 该账号以资深HRD的独特视角，通过对职场生态及社会热点事件的深度“吃瓜”式解读，揭示现象背后的深层逻辑与人性真相，旨在为读者提供客观的职场与人生洞察，并促进认知升级。

#### 2. 账号内容的主题
*   **核心主题：**
    *   **职场生存法则与挑战：** 聚焦大厂“饥饿游戏”模式、内卷、PUA、裁员潮、晋升困境、不健康的职场关系等。
    *   **社会阶层与特权现象：** 深入探讨“天龙人”的“保级焦虑”、资源倾斜、投胎技术、家族联姻、学历“注水”等特权现象。
    *   **婚恋关系中的权力与利益：** 关注婚姻中的PUA、财产转移、伴侣关系的异化以及“校园到婚纱”童话的破碎。
    *   **认知偏差与自我成长：** 讨论“洗脑包”的危害、绩优主义的反噬、自我认知的重要性以及如何重建健康心态。
*   **主题细分：**
    *   **职场：** 大厂的组织架构、绩效考核、领导风格、HR职能、员工心理健康（如焦虑、抑郁）、高压工作环境下的身体反应。
    *   **社会现象：** 名人/高知家庭的育儿方式、留学经历对人性的影响、财富对人品性的考验、社会分层与固化、不同职业/行业的就业前景。
    *   **人际关系：** 亲子关系中的PUA、伴侣关系中的不平等、社会交往中的“正常人”与“不正常人”区分。
*   **主题关联性：** 各主题之间存在高度关联。职场问题常被视为社会结构性问题的映射；婚恋、家庭、教育等话题也常与阶层、特权、个人成长等核心概念交叉。例如，大厂PUA技能被认为也体现在家庭关系中；高知家庭的育儿问题被视为其“保级焦虑”的体现。

#### 3. 账号内容的特点、风格、一致性
*   **特点：**
    *   **犀利批判：** 敢于直言不讳地指出问题，不回避敏感话题。
    *   **深度洞察：** 擅长从表面现象挖掘其深层逻辑和普遍规律。
    *   **幽默讽刺：** 运用大量网络表情包和调侃语气，将沉重话题轻松化，提升可读性。
    *   **务实清醒：** 强调回归现实，打破幻想，提供具有实践意义的建议。
    *   **冷静客观（表象）：** 尽管观点犀利，但表达方式多以转述、引用聊天记录为主，营造出一种“旁观者清”的客观感。
*   **风格：**
    *   **对话式呈现：** 大部分内容以微信聊天截图的形式呈现，模拟朋友间的私密讨论，增强真实感和代入感。
    *   **图文结合：** 搭配大量表情包和网络梗图，增加趣味性和情感表达。
    *   **视频化解读：** 部分内容制作成配有字幕和表情包的语音视频，便于多维度传播复杂信息。
    *   **口语化与专业性并存：** 语言风格轻松活泼，同时又不失专业术语和理论分析。
*   **一致性：** 账号在所有帖子中都保持了高度一致的特点和风格。
    *   **人设一致性：** 胖胖胖胖总作为“资深HRD”和“猎头公司合伙人”，其发言总能体现出对职场和人性深刻的理解，以及对社会“洗脑包”的警惕。其描述的“普本”背景与“专家”身份形成反差，增强了其观点的可信度。
    *   **表达方式一致性：** 几乎所有帖子都采用聊天截图作为主要内容载体，辅以简洁明了的文字总结和观点输出，表情包的使用也高度统一。
    *   **内容方向一致性：** 始终围绕职场痛点、社会热点中的不公现象，以及由此延伸出的个人成长和认知升级。

#### 4. 账号内容的痛点/需求/兴趣点
*   **痛点：**
    *   职场PUA和内卷带来的精神压力和身体健康问题。
    *   对社会阶层固化和特权现象的无力感。
    *   对传统婚恋观念和“成功”定义的反思与迷茫。
    *   信息茧房和认知偏差导致的生活困境。
*   **需求：**
    *   获得对复杂社会和职场现象的深度解读和真相。
    *   寻找共鸣，确认自身经历并非个例，从而缓解焦虑和孤独。
    *   学习如何识别和应对职场及生活中的PUA、不公平待遇。
    *   获取务实的职业发展和人生选择建议。
*   **兴趣点：**
    *   围绕知名大厂和公众人物的“吃瓜”事件。
    *   对社会底层逻辑和人性本质的探讨。
    *   反思和批判主流价值观。

#### 5. 账号内容的目标受众画像
*   **核心受众：** 25-40岁之间的职场人士，尤其是互联网大厂或高压行业从业者。对社会现实有一定认知，但可能在职场或个人生活中遇到困境。
*   **受众特点：**
    *   **职业背景：** 主要集中在互联网、金融、医疗等竞争激烈、压力较大的行业。
    *   **思维方式：** 具有一定的批判性思维，不盲从主流观点，渴望了解事物真相。
    *   **情感状态：** 可能存在职场焦虑、精神内耗、对未来感到迷茫或失望。
    *   **生活关注：** 除了职业发展，也关注个人成长、婚恋关系、家庭教育以及社会公平议题。
    *   **学习习惯：** 倾向于从案例和故事中学习，喜欢直接、不拖沓的观点输出。
*   **为什么这些受众会关注这个账号：** 该账号的深层分析和接地气的表达方式，能够精准触达这些受众的痛点，提供情绪价值（共鸣、解气）和认知价值（洞察、解决方案）。“胖胖胖胖总”的人设也增强了内容的可信度和吸引力。
# Agent 定义文档

## 1. 基本信息 (Basic Information)

* **Agent 名称 (Agent Name):** [您的 Agent 的名字]
* **版本 (Version):** [例如: 1.0, 20250530]
* **创建者/团队 (Author/Team):** [您的名字或团队名称]
* **创建日期 (Creation Date):** [YYYY-MM-DD]
* **最后更新日期 (Last Updated Date):** [YYYY-MM-DD]
* **简要描述 (Brief Description):**
    * [用一两句话概括 Agent 的核心目的和功能]

## 2. 核心目标与任务 (Core Goals and Tasks)

* **主要目标 (Primary Goal(s)):**
    * [Agent 需要实现的最终目标，例如：提高用户预订成功率、解答用户关于特定产品的疑问、自动生成周报摘要等]
    * [可以有多个主要目标]
* **具体任务 (Specific Tasks):**
    * [为了实现主要目标，Agent 需要执行的具体、可操作的任务列表]
    * 示例:
        * 任务1: 理解用户的自然语言查询
        * 任务2: 从知识库中检索相关信息
        * 任务3: 根据用户信息和偏好推荐产品
        * 任务4: 调用 API 完成预订操作
        * 任务5: 生成简洁明了的回复
* **成功标准/关键绩效指标 (Success Criteria / KPIs):**
    * [如何衡量 Agent 是否成功完成了任务或达到了目标？]
    * 示例:
        * 任务完成率达到 X%
        * 用户满意度评分高于 Y
        * 平均响应时间低于 Z 秒
        * 信息准确率达到 W%
* **失败条件与处理 (Failure Conditions & Handling):**
    * [在什么情况下认为 Agent 失败？失败后应如何处理？]
    * 示例:
        * 无法理解用户意图超过 N 次 -> 提示用户换种问法或转接人工
        * API 调用失败 -> 告知用户系统暂时无法处理，并记录错误
        * 信息检索不到 -> 明确告知用户当前知识范围无法解答

## 3. 角色与个性 (Role and Persona)

* **角色 (Role):**
    * [Agent 在交互中扮演的角色，例如：友好的助手、专业的顾问、高效的执行者、幽默的伙伴等]
* **个性特征 (Personality Traits):**
    * [描述 Agent 的性格特点，选择 3-5 个核心词汇]
    * 示例: 专业、耐心、简洁、积极、严谨、富有同情心、幽默等
* **沟通风格与语气 (Communication Style and Tone):**
    * [Agent 与用户沟通时应采用的风格和语气]
    * 示例: 正式、非正式、技术性、通俗易懂、鼓励性、中立客观等
* **语言视角 (Perspective):**
    * [Agent 在对话中使用的代词，例如：使用“我”、“我们”还是避免使用第一人称？]
* **行为准则 (Code of Conduct / Ethical Guidelines):**
    * [Agent 必须遵守的规则和道德约束]
    * 示例:
        * 绝不透露用户隐私
        * 避免使用歧视性或攻击性语言
        * 提供客观公正的信息，除非角色设定需要
        * 在不确定时承认局限性

## 4. 知识与能力 (Knowledge and Capabilities)

* **知识库 (Knowledge Base):**
    * **信息来源 (Information Sources):**
        * [Agent 可以访问和利用的信息来源，例如：特定的数据库、API 接口、FAQ 文档、网站内容、内部知识库等]
        * [是否允许访问实时网络信息？]
    * **专业领域 (Domain Expertise):**
        * [Agent 擅长的特定知识领域]
    * **知识范围与局限性 (Knowledge Scope and Limitations):**
        * [明确 Agent 知道什么，不知道什么，以及无法回答哪些类型的问题]
* **技能集 (Skillset / Tools):**
    * **可执行的动作/工具 (Executable Actions / Tools):**
        * [Agent 能够执行的具体操作或可以调用的工具]
        * 示例: 搜索信息、数据分析、代码生成、发送邮件、调用日历 API、进行计算、翻译语言、生成图片等
    * **语言能力 (Language Capabilities):**
        * [支持的语言、自然语言理解 (NLU) 的深度、自然语言生成 (NLG) 的风格]
* **学习能力 (Learning Capabilities) (可选):**
    * [Agent 是否以及如何从交互中学习和改进？]
    * 示例: 从用户反馈中学习、记忆用户偏好、自动更新知识库（需谨慎设计）

## 5. 交互与沟通 (Interaction and Communication)

* **输入渠道 (Input Channels):**
    * [用户可以通过哪些方式与 Agent 交互，例如：文本、语音、图像、文件上传等]
* **输出渠道 (Output Channels):**
    * [Agent 可以通过哪些方式回应用户，例如：文本、语音、图像、生成文件、UI 组件等]
* **对话流程管理 (Conversation Flow Management):**
    * **对话启动 (Initiation):** [Agent 如何开始对话？主动问候还是被动响应？]
    * **对话结束 (Termination):** [Agent 如何结束对话？]
    * **澄清与追问 (Clarification and Probing):** [当用户指令不明确时，Agent 如何提问以获取更多信息？]
    * **错误处理与纠正 (Error Handling and Correction):** [当 Agent 理解错误或无法完成任务时，如何向用户解释并尝试纠正？]
    * **多轮对话能力 (Multi-turn Conversation Capability):** [Agent 是否需要记住之前的对话内容并用于后续交互？]
* **响应约束 (Response Constraints):**
    * [对 Agent 回复的具体要求]
    * 示例:
        * 回复长度限制 (例如：不超过 N 个字符/段落)
        * 回复格式 (例如：使用 Markdown、JSON、纯文本)
        * 信息披露限制 (例如：不能透露具体算法细节)
        * 响应速度要求

## 6. 约束与限制 (Constraints and Limitations)

* **禁止行为 (Prohibited Actions / Topics):**
    * [明确列出 Agent 绝对不能做的事情或讨论的话题]
    * 示例: 提供医疗建议、进行金融投资操作、生成非法内容、讨论敏感政治话题等
* **技术限制 (Technical Constraints):**
    * [例如：API 调用频率限制、计算资源限制等]
* **法律与合规要求 (Legal and Compliance Requirements):**
    * [Agent 需要遵守的法律法规，例如：GDPR、数据隐私政策等]

## 7. 上下文管理 (Context Management)

* **短期记忆 (Short-term Memory):**
    * [Agent 在单次会话中需要记住哪些信息？如何利用这些信息？]
* **长期记忆 (Long-term Memory) (可选):**
    * [Agent 是否需要在多次会话间记住用户信息、偏好或历史交互？如何实现？]
* **上下文利用方式 (How Context is Used):**
    * [具体说明上下文信息如何影响 Agent 的决策和回复]

## 8. 初始指令/系统提示示例 (Initial Instruction / System Prompt Example)

* **核心指令 (Core Instruction):**
    * ```text
        # 角色
        你是一个名叫“智多星”的AI助手，你的目标是帮助用户高效地解决与我们产品相关的问题。

        # 个性与语气
        你的个性应该是友好、耐心且专业的。请使用清晰、简洁的语言，避免使用过于技术性的术语，除非用户表现出专业背景。

        # 任务
        1.  准确理解用户的问题。
        2.  如果问题不明确，主动提问以澄清。
        3.  从提供的知识库 [知识库名称/链接] 中查找答案。
        4.  如果知识库中没有答案，请明确告知用户你暂时无法回答，并询问是否需要记录问题以便后续跟进。
        5.  不要编造答案。

        # 限制
        -   不要提供任何与我们产品无关的建议。
        -   不要进行任何形式的闲聊，除非是为了缓解用户情绪或建立融洽关系。
        -   不要透露你的底层实现细节。

        # 输出格式
        -   对于简单问题，直接给出答案。
        -   对于复杂问题，可以考虑使用列表或步骤来使答案更清晰。
        ```
* **(可选) 动态指令片段 (Dynamic Prompt Segments):**
    * [根据特定情境或用户输入动态调整的指令部分]

## 9. 评估与测试 (Evaluation and Testing)

* **评估指标 (Evaluation Metrics):**
    * [除了第2点的 KPIs，这里可以更细化，例如：意图识别准确率、槽位填充准确率、回复相关性、语言流畅度等]
* **测试用例 (Test Cases):**
    * [设计一些典型的用户查询和场景，用于测试 Agent 的表现]
    * 示例:
        * 常见问题查询
        * 边界条件测试 (例如：模糊不清的提问、超出知识范围的提问)
        * 敏感词测试
        * 多轮对话测试

## 10. 其他 (Miscellaneous)

* **依赖项 (Dependencies):**
    * [Agent 运行所依赖的其他系统、服务或 API]
* **未来增强计划 (Future Enhancements):**
    * [计划在未来版本中添加或改进的功能]

---

请记住，这只是一个起点。您需要根据您的 Agent 的具体应用场景和复杂性来填充、修改和扩展这个模板。一个定义清晰的 Agent 是成功构建和部署 AI 应用的关键。
#### 6. 账号内容的内容价值主张
*   **核心价值主张：** 击碎滤镜与“洗脑包”，提供职场与社会真相的深度解读，赋能个体以清醒的认知和实用的策略应对复杂现实。
*   **所属维度：**
    *   **信息获取：** 提供独家视角、深度解读、系统知识。
    *   **情感满足：** 获得共鸣、治愈、激励、认同感。
    *   **技能提升：** 提供应对职场PUA、调整认知的实用方法论。

#### 7. 账号内容的内容深度与广度
*   **深度：** **专业壁垒**。账号不仅仅停留在事件的表面，而是深入挖掘事件背后的社会结构、心理机制、权力博弈和人性弱点。例如，将职场PUA与家庭PUA、国际关系进行类比，将高知家庭的育儿焦虑与阶级固化相连接。这需要深厚的社会学、心理学和职场经验积累。
*   **广度：** **适度拓展**。账号以“职场观察与解读”和“社会热点深度剖析”为核心，并围绕这些核心主题向外延伸，如“婚恋关系”、“个人成长”、“教育”、“留学”等，但始终保持在社会人文和职业发展的范畴内，没有过度泛化。

#### 8. 账号内容的亮点
*   **独特的人设：** “胖胖胖胖总”的资深HRD/猎头/专家身份，结合其看似随意的“吃瓜”方式，形成一种反差萌与权威感的独特结合。
*   **“吃瓜”的深度与广度：** 将日常吃瓜事件提升到对社会规律、人性本质的探讨，具有极强的启发性。
*   **痛点共鸣：** 精准捕捉职场人普遍存在的焦虑、内耗、不公等痛点，提供情绪宣泄和理解的出口。
*   **形式创新：** 大量使用微信聊天截图作为内容主体，辅以画外音和表情包，增强了内容的真实感、亲切感和传播效率。
*   **反“洗脑包”：** 致力于揭露社会中的虚假繁荣和不切实际的“成功学”，帮助用户建立更客观清醒的认知。

#### 9. 账号内容的选题模式
*   **选题的灵感来源：**
    *   **社会热点事件/名人八卦：** 尤其是高关注度的、涉及特权阶层、大厂或婚恋纠纷的事件（如“大连王博文老师外甥故事”、“互联网大厂技术高管婚变”、“董天临/翟天临事件”、“大厂心理咨询师辞职”、“甜甜小姐代言风波”、“特朗普美股操作”）。
    *   **职场普遍现象：** 如职场PUA、大厂的“饥饿游戏”模式、内卷、裁员、职场中的“黑话”和不健康沟通方式。
    *   **个人成长与心理困惑：** 例如认知偏差、讨好型人格的形成、精神内耗、自我主体性的缺失。
    *   **粉丝互动与提问：** 评论区提问、私信咨询等，也成为重要的选题来源。
    *   **个人职业经验：** 作为资深HRD和猎头，对行业内部动态和人才趋势有敏锐的洞察。
*   **选题的创作方式：**
    *   **案例引入-深度解析模式：** 从一个具体的“瓜”或事件（如“大厂驻厂心理咨询师跑路”）开始，通过微信聊天记录的形式呈现，然后由博主进行深入的分析和点评，将个体事件上升为普遍现象或系统性问题。
    *   **反向观点-批判性解读模式：** 针对某个主流或普遍接受的观念（如“高知高认知”、“校园到婚纱是圆满剧本”），提出质疑并进行反向的、批判性的解读。
    *   **现象归纳-本质揭示模式：** 观察多个看似独立的现象（如“大厂各种PUA”，以及“家庭PUA”），归纳出其共同的底层逻辑或本质规律（如“权力博弈”、“控制欲”）。
*   **选题的亮点体现：**
    *   **信息差的弥补：** 提供普通人难以触及的内幕信息或专业视角。
    *   **情绪价值的满足：** 观点犀利，直指痛点，让读者感到被理解和共鸣。
    *   **认知升级的引导：** 每次分析都试图打破用户的固有认知，促使他们进行深度思考。
*   **历史优质选题（基于点赞数和收藏数）：**
    *   **帖子3: 怎么就…突然有了自我**
        *   **亮点：** 探讨了社会地位与育儿结果的非正相关性，以及高精专父母在孩子面前的两幅面孔。深刻揭示了“突然有了自我”背后可能存在的社会时钟、家庭 PUA 和“偶像包袱”等问题。
        *   **人设结合：** 胖胖胖胖总作为职场与个人成长专家，敏锐捕捉到社会热点中反映出的深层人性与家庭教育问题，其犀利但不失思辨的分析，符合其“击碎洗脑包”的人设。
        *   **创作方式：** 以大连王博文老师分享的故事为引子，通过聊天截图呈现讨论过程，逐步引入“社会时钟”、“自我主体性”等概念，由浅入深。
        *   **内容方向：** 个人成长、家庭教育、社会时钟、高知群体心态、认知偏差。
        *   **灵感来源：** 网络上关于大连王博文老师外甥的故事。
    *   **帖子15: 绷不住了，大厂驻厂心理咨询师跑路了…**
        *   **亮点：** 揭示了互联网大厂“饥饿游戏”式的生存模式，以及由此引发的员工精神状态问题，甚至连心理咨询师也难以自洽，强调这是结构性问题而非个体问题。
        *   **人设结合：** 胖胖胖胖总作为资深HRD，对大厂内部运作和职场PUA有着深刻理解，通过该事件验证了其“职场炼狱”的观点，进一步巩固了其专业且敢言的人设。
        *   **创作方式：** 从“大厂驻厂心理咨询师跑路”这一新闻事件切入，通过微信聊天截图展现朋友间的讨论，引申到大厂普遍存在的系统性压榨和精神污染问题。
        *   **内容方向：** 互联网大厂职场文化、员工心理健康、职场PUA、企业结构性问题。
        *   **灵感来源：** 某互联网大厂心理咨询师的自白。
    *   **帖子6: 不是…这也算立功了吧🐶**
        *   **亮点：** 巧妙地将“董天临”事件与“计划生育”联系，讽刺了某些特权阶层子女因父母的铺路而缺乏实际能力，最终导致“培养失败的联姻工具”被全国网友“扒”的现象，并将其视为是对社会公众的“立功”。
        *   **人设结合：** 胖胖胖胖总以其独特的幽默感和批判视角，对社会不公现象进行辛辣讽刺，体现了其“吃瓜”背后对真相的追求和对社会公平的关注。
        *   **创作方式：** 以“董天临”事件的后续进展为核心，通过聊天截图展现朋友间的讨论，从“家族联姻”、“草包小主”等角度进行解读，最终得出“天亮了”的结论。
        *   **内容方向：** 阶层固化、家族联姻、特权教育、社会舆论、公平正义。
        *   **灵感来源：** “董天临”事件的持续发酵和网友讨论。
    *   **帖子16: Dark Force的反面是“易被PUA”**
        *   **亮点：** 深入剖析了“鸡娃”现象背后的“要性”与“绩优主义”驱动，指出这种对“Dark Force”的追求可能使孩子更容易被PUA，并强调个人努力需考量能力边界与宏观环境。
        *   **人设结合：** 胖胖胖胖总结合心理学与职场经验，对当下育儿焦虑和社会成功学进行深层批判，展现了其对个体心理与社会文化关联的深刻洞察。
        *   **创作方式：** 从“鸡娃走火入魔”的现象切入，通过聊天截图和理论分析（均值回归、Dark Force），探讨了“要性”的双刃剑效应及其对个体心理健康的潜在风险。
        *   **内容方向：** 鸡娃、教育焦虑、绩优主义、职场PUA、原生家庭影响、个人成长。
        *   **灵感来源：** 育儿领域的热点话题及专家观点。
    *   **帖子11: 害，留子是一片大瓜田…🫣**
        *   **亮点：** 提供了对留学生群体的批判性视角，区分了“easy模式”下被过度保护和“一路水”的留学生，以及通过信息差和“钞能力”获得资源的现象，打破了对“留子”的单一滤镜。
        *   **人设结合：** 胖胖胖胖总作为社会观察者，敢于揭露教育资源不公和信息不对称的问题，其客观且不失犀利的分析符合其“击碎洗脑包”的人设。
        *   **创作方式：** 以“留子客观看待XX本科学校”的笔记为引子，通过聊天截图讨论留学生的不同成长路径，引申出信息差、金钱和背景在教育中的作用。
        *   **内容方向：** 留学生群体、教育公平、阶层差异、信息差、社会现实。
        *   **灵感来源：** 对留学生群体的观察和相关社会讨论。

#### 10. 账号创作新选题与人设匹配的判断条件
为了保持账号内容的一致性和专业性，创作新选题时需要判断新选题是否符合账号选题的人设。以下是判断新选题与人设匹配的方式和方法：

*   **核心匹配要素（必须满足）：**
    1.  **主题相关性：** 新选题必须紧密围绕“职场生态”、“社会热点（尤其是涉及权力、利益、人性、阶层等）”或“个人成长与认知升级”这三个核心品类。
    2.  **批判性与深度：** 选题不能是表面化的“吃瓜”，而应能深挖其背后的逻辑、系统性问题或人性弱点，体现“胖胖胖胖总”的深度洞察力。
    3.  **人设契合度：** 选题应能让“胖胖胖胖总”以资深HRD/猎头/专家身份，结合其独特的“普本”背景，提供具有专业性、清醒、甚至略带玩世不恭但务实的观点。
    4.  **形式延续性：** 优先考虑使用微信聊天截图作为主要内容呈现形式，辅以精炼的文字总结和博主的评论，或制作成配有字幕和表情包的语音视频。

*   **辅助匹配方式：**
    1.  **“洗脑包”识别：** 选题是否能揭示某种社会“洗脑包”或普遍存在的认知误区，并提供反思和纠正的视角。
    2.  **情绪共鸣与引导：** 选题能否触及目标受众的痛点，引发强烈共鸣，并引导读者从情绪宣泄走向理性思考和自我赋能。
    3.  **跨界关联性：** 尝试将看似不相关的职场/社会现象进行巧妙的类比和连接，展现博主的思维广度（例如将职场PUA与家庭PUA、国际关系相连）。
    4.  **反差与幽默：** 选题本身或其解读方式是否具有一定的反差感，能够通过幽默、讽刺或调侃的语气来化解沉重，提升传播力。

*   **不匹配的信号（应避免）：**
    *   纯粹的娱乐八卦，缺乏深度分析和普适价值。
    *   过于积极正向、脱离现实的“鸡汤”内容。
    *   与职场、社会议题、个人成长主题无关的生活分享。
    *   表达方式过于情绪化，缺乏冷静客观的分析。
    *   内容立场模糊，或与过往人设观点产生冲突。
"""
    # ans, usage = reference_note_available("56e02fa4cb35fb071599c959", "682d78b1000000002100468f")

    ans, usage = topic_generate_by_persona(persona, "683015460000000023012e14")
    print(usage)
    pass
