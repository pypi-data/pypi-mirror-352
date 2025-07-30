import json
import aiddit.utils as utils
import os
import aiddit.model.google_genai as google_genai


def extract_topic_result(topic_result):
    prompt = f"""我会给你一数据，你提取其中的选题结果和选题的详细说明出来，不要修改任何文字。但如果文字中有类似 markdown 的加粗符号，需要去掉。注意：选题的详细说明为标题后的第一段话
返回一个json对象，- output in JSON format with keys:topicResult、topicDescription
以下是我的信息

```
{topic_result}
```
"""

    conversation_user_message = google_genai.GenaiConversationMessage.one("user", prompt)

    ans_message = google_genai.google_genai_output_images_and_text(new_message=conversation_user_message,
                                                                   model=google_genai.MODEL_GEMINI_2_0_FLASH,
                                                                   response_mime_type="application/json")

    ans_content = ans_message.content[0].value

    return utils.try_remove_markdown_tag_and_to_json(ans_content)


if __name__ == "__main__":
    dir_path = "/Users/nieqi/Documents/workspace/python/image_article_comprehension/aigc_data/agent_record/opt_0528"
    records = utils.load_from_json_dir(dir_path)

    for record in records:
        if record.get("opt_result") is None:
            continue

        save_file_name = f"{record.get('agent_exe_id')}.json"
        if record.get("topic_result") is not None and record.get("extract_topic_result") is None:
            record["extract_topic_result"] = extract_topic_result(record.get("topic_result"))
            utils.save(record, os.path.join(dir_path, save_file_name))

        if record.get("opt_result") is not None and record.get("opt_result").get("topic_result") is not None and record.get(
                "opt_result").get("extract_topic_result") is None:
            record["opt_result"]["extract_topic_result"] = extract_topic_result(record.get("opt_result").get("topic_result"))
            utils.save(record, os.path.join(dir_path, save_file_name))

    pass
