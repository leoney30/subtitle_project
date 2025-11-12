import srt
import os
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import re
'''1:检索所有说话人,也就是字幕文件文本的第一个":"前的文本内容,即是说话人,如果字幕块没有标识说话人,即代表此字幕块为上一个字幕块的说话人,遍历全部字幕,整合出所有说话人
    2:将此说话人的所有字幕块重新整合为一个新的srt文件,输出到源文件目录'''
def select_srt_file():
    """
    弹出一个文件选择框，选择一个 .srt 文件。
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    filepath = filedialog.askopenfilename(
        title="请选择 SRT 字幕文件",
        filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
    )
    
    if not filepath:
        print("未选择文件，程序退出。")
        return None
        
    return filepath

def process_srt_file(filepath):
    """
    主处理函数，用于解析、分离和写入新的 SRT 文件。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    try:
        subs = list(srt.parse(content))
    except Exception as e:
        print(f"解析 SRT 文件 {filepath} 时出错，请检查文件格式。")
        print(f"错误详情: {e}")
        return

    speaker_subs = defaultdict(list)
    # 默认说话人，用于处理在第一个说话人出现之前的任何字幕
    current_speaker = "UNKNOWN"  

    print("开始处理字幕...")

    for sub in subs:
        # 获取字幕内容，并去除前后的空白（如换行符）
        text = sub.content.strip()
        
        if not text:
            # 如果字幕块为空，则跳过
            continue

        lines = text.splitlines()
        first_line = lines[0].strip()
        
        # 尝试在第一行按冒号分割
        parts = first_line.split(':', 1)

        # --- 核心逻辑：检查说话人 ---
        # 1. 必须在第一行找到冒号 (len(parts) == 2)
        # 2. 冒号前的文本 (parts[0]) strip() 后必须不为空
        # 3. 冒号前的文本 (parts[0]) 必须全部为大写 (isupper())
        
        speaker_tag = parts[0].strip()
        
        if len(parts) == 2 and speaker_tag and speaker_tag.isupper():
            # 这是一个新的说话人标签！
            current_speaker = speaker_tag  # 更新当前说话人
                    
        else:
            # 这不是一个新的说话人标签
            # 保持 sub.content 不变，它将归属于 current_speaker
            pass

        # 将处理后的字幕块（无论是否修改过）添加到对应说话人的列表
        speaker_subs[current_speaker].append(sub)

    if not speaker_subs:
        print("未在文件中找到任何字幕。")
        return

    print(f"识别到 {len(speaker_subs)} 位说话人: {', '.join(speaker_subs.keys())}")

    # --- 写入新的 SRT 文件 ---
    output_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]

    for speaker, subs_list in speaker_subs.items():
        # 过滤掉空的字幕块（如果移除标签后变为空）
        valid_subs = [s for s in subs_list if s.content.strip()]
        
        if not valid_subs:
            print(f"说话人 {speaker} 没有有效字幕内容，已跳过。")
            continue

        # 重新编号字幕索引
        new_srt_content = srt.compose(valid_subs)
        
        # 清理文件名中的非法字符
        safe_speaker_name = re.sub(r'[\\/*?:"<>|]', '_', speaker)
        output_filename = f"{base_name}_{safe_speaker_name}.srt"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_srt_content)
            print(f"已为“{speaker}”创建文件: {output_path}")
        except Exception as e:
            print(f"为“{speaker}”写入文件时出错: {e}")

    print("\n处理完成。")

# --- 脚本主入口 ---
if __name__ == "__main__":
    srt_file_path = select_srt_file()
    
    if srt_file_path:
        process_srt_file(srt_file_path)