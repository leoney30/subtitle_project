import os
import webbrowser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def choose_file():
    Tk().withdraw()
    return askopenfilename()

def split_srt(input_file, output_folder):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')
    
    chunk_size = 50  # 分割序号
    num_chunks = (len(lines) + chunk_size - 1) // chunk_size

    os.makedirs(output_folder, exist_ok=True)

    html_code = "<html>\n<body>\n"
    buttons_html = "复制按钮:<br/>\n"

    file_infos = []
    chunks_data = []
    for chunk_index in range(num_chunks):
        start_index = chunk_index * chunk_size
        end_index = min((chunk_index + 1) * chunk_size, len(lines))
        chunk_data = "\n\n".join(lines[start_index:end_index])

        first_line = chunk_data.split('\n')[0]  # 获取开始序号
        last_line = ""  # 初始化结束序号

        # 正确获取结束序号
        for line in reversed(chunk_data.split('\n\n')):
            if line.strip() and line.strip().split('\n')[0].isdigit():
                last_line = line.strip().split('\n')[0]
                break

        file_info = f"文件 {chunk_index+1}, 序号: {first_line} - {last_line}"
        file_infos.append(file_info)

        chunks_data.append(chunk_data)

    # 验证最后一个块的大小，确保它不少于30个序号
    if len(chunks_data[-1].split('\n\n')) < 30 and len(chunks_data) > 1:
        # 将最后一个块的数据合并到倒数第二个块中
        chunks_data[-2] += "\n\n" + chunks_data[-1]
        chunks_data.pop(-1)  # 移除最后一个块
        file_infos[-2] = file_infos[-1]   # 修正倒数第二个文件信息
        file_infos.pop(-1)  # 移除最后一个文件信息


    for index, file_info in enumerate(file_infos):
        buttons_html += f'<button onClick="myFunction(\'area_{index}\')">{file_info}</button><br/>\n'
    html_code += buttons_html

    for chunk_index, chunk_data in enumerate(chunks_data):
        file_info = file_infos[chunk_index]
        html_code += f"<h3>{file_info}</h3>\n"
        html_code += f'<textarea id="area_{chunk_index}" rows="10" cols="80">{chunk_data}</textarea><br/>\n'

    html_code += """
    <script>
    function myFunction(id) {
      var copyText = document.getElementById(id);
      copyText.select();
      copyText.setSelectionRange(0, 99999);
      document.execCommand("copy");
    }
    </script>
    </body>
    </html>
    """

    html_file = os.path.join(output_folder, "output.html")
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(html_code)

    webbrowser.open('file://' + os.path.realpath(html_file))

if __name__ == "__main__":
    input_file = choose_file() # 用户选择SRT文件
    output_folder = "字幕分割"

    split_srt(input_file, output_folder)
    print(f"分割完成! 请在<{output_folder}>文件夹中查看'output.html'文件。")
    print(f"output.html文件路径: {os.path.realpath('output.html')}")