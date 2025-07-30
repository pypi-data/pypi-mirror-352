import sys

sys.path.append("/Users/nieqi/Documents/workspace/python")
from image_analyzer.utils.feshu import write_data_to_sheet
import aiddit.api.xhs_api as xhs_api
import pandas as pd
import os
import json
from itertools import groupby
import pandas
import aiddit.utils as utils


# Directory containing the data files
data_dir = '/Users/nieqi/Documents/workspace/python/image_article_comprehension/aigc_data/agent_record/opt_0528'
data = []

all_result = utils.load_from_json_dir(data_dir)

for result in all_result:
    try:
        if result.get("opt_result") is None:
            continue

        reference_note_id = result.get("reference_note_id")
        xhs_user_id = result.get("xhs_user_id")

        note = xhs_api._get_note_detail_by_id(reference_note_id)
        account_info = xhs_api._get_xhs_account_info(xhs_user_id)

        images = [f"\"{i}\"" for i in utils.remove_duplicates(note.get("images", []))]

        opt = result.get("opt_result", {})

        row = {
            "账号名": account_info.get("account_name", ""),
            "账号链接": account_info.get("account_link", ""),
            "刺激源链接": note.get("link", ""),
            "刺激源": f"{note.get('title')}\n\n{note.get('body_text', '')}",
            '刺激源图片': f"[{','.join(images)}]",

            "Agent执行记录": f"http://aigc-admin.cybertogether.net/generate/agent/record?agentExeId={result.get('agent_exe_id')}&filters=%7B%7D",
            "能否产生选题": result.get("status"),
            "选题": result.get("extract_topic_result", {}).get("topicResult"),
            "选题说明": result.get("extract_topic_result", {}).get("topicDescription"),
            "灵感创作判断输出": result.get("available_result"),
            "选题判断输出": result.get("topic_result"),

            "优化_能否产生选题": opt.get("status"),
            "优化_选题": opt.get("extract_topic_result", {}).get("topicResult"),
            "优化_选题说明": opt.get("extract_topic_result", {}).get("topicDescription"),
            "优化_灵感创作判断输出": opt.get("available_result"),
            "优化_选题判断输出": opt.get("topic_result"),
        }
        data.append(row)
    except Exception as e:
        print(e)

# Convert DataFrame to list with header
df = pd.DataFrame(data)
header = df.columns.tolist()
data_rows = df.values.tolist()
data_with_header = [header] + data_rows

sheet_token = 'Ty2MsTOSih0B2KtSdAAczl5fnJe'
sheet_id = '382VMO'

write_data_to_sheet(data_with_header, sheet_token=sheet_token,
                    sheetid=sheet_id, )
