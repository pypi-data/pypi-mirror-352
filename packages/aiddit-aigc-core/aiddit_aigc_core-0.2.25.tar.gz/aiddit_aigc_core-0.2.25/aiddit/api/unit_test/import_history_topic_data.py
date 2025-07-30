import os.path

import pandas as pd
import json
import aiddit.utils as utils

data_path = "/Users/nieqi/Downloads/agent.csv"

if __name__ == "__main__":
    df = pd.read_csv(data_path)
    # 打印数据
    print(df)
    # 将数据转换为字典
    data_dict = df.to_dict(orient="records")  # 每行作为一个字典

    save_dir = "/Users/nieqi/Documents/workspace/python/image_article_comprehension/aigc_data/agent_record/opt_0528"

    for d in data_dict:
        save_file_name = f"{d.get('agent_exe_id')}.json"

        exe_data = json.loads(json.loads(d.get("exe_data")).get("arguments"))

        reference_note_id = exe_data.get("reference_note_id")

        if len(reference_note_id) != len("6810bd1c0000000009014800"):
            continue

        save_data = {
            "agent_exe_id": d.get("agent_exe_id"),
            "status": "无法产生选题" if d.get("status") == "stopCondition" else "可产生选题",
            "xhs_user_id": exe_data.get("xhs_user_id"),
            "reference_note_id": reference_note_id,
            "available_result": d.get("result"),
            "topic_result": d.get("final_result") if d.get("status") == "success" else None,
            "exe_timestamp": d.get("update_timestamp")
        }

        utils.save(save_data, os.path.join(save_dir, save_file_name))
    pass
