import os
import webbrowser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def choose_file():
    Tk().withdraw()
    return askopenfilename()

def simplify_srt(input_file, output_folder):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')

    # 1. 删除100个字幕块之后的短字幕块（仅计算字幕文本部分的长度）
    filtered_lines = []
    for block in lines:
        parts = block.split('\n')
        if len(parts) > 2:  # 确保有序号、时间戳和至少一行字幕文本
            text_content = ' '.join(parts[2:])  # 组合所有字幕文本行
            if len(filtered_lines) < 100 or len(text_content) >= 15:
                filtered_lines.append(block)

    # 2. 删除前100个字幕块中的最后20个
    filtered_lines = filtered_lines[:80] + filtered_lines[100:]

    # 3. 如果超过400个字幕块，则删除多余部分
    if len(filtered_lines) > 400:
        excess_blocks = len(filtered_lines) - 400
        delete_interval = len(filtered_lines) // excess_blocks

        simplified_lines = []
        for i in range(len(filtered_lines)):
            if i % delete_interval != 0:
                simplified_lines.append(filtered_lines[i])
    else:
        simplified_lines = filtered_lines

    # 4. 保持原始序号并保留时间戳的开始时间
    updated_lines = []
    for block in simplified_lines:
        parts = block.split('\n')
        original_index = parts[0]  # 保持原始序号
        
        # 提取并简化时间戳
        timestamp = parts[1].split(' --> ')[0]  # 只保留开始时间
        parts[1] = timestamp  # 更新时间戳
        
        updated_lines.append('\n'.join(parts))

    # 5. 将精简后的字幕嵌入到 HTML 中
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "simplified.html")

    html_content = """
    <html>
    <body>
        <h3>精简后字幕块数量: {}</h3>
        <textarea rows="30" cols="80">{}</textarea>
    </body>
    </html>
    """
    html_content = html_content.format(len(updated_lines), "\n\n".join(updated_lines))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 6. 自动打开 HTML 文件
    webbrowser.open('file://' + os.path.realpath(output_file))

    print(f"字幕精简完成! HTML 文件已保存到: {output_file}")

if __name__ == "__main__":
    input_file = choose_file()
    output_folder = "字幕精简"

    simplify_srt(input_file, output_folder)
