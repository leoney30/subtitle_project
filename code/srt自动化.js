// srt自动化脚本
let lastMessageCount = 0;
let timerId = null;
let chunks;
let index = 0;
// SRT文件地址
const SRT_FILE_NAME = '20250903sca发布会/sca发布会.srt';
// const SRT_FILE_URL = `https://raw.githubusercontent.com/leoney30/Subtitle_project/main/subtitle/${SRT_FILE_NAME}/${SRT_FILE_NAME}.srt`;
const SRT_FILE_URL = `https://raw.githubusercontent.com/leoney30/subtitle_project/main/subtitle/${SRT_FILE_NAME}`;
// const SRT_FILE_URL = `https://raw.githubusercontent.com/leoney30/Subtitle_project/main/test57.srt`;



// 获取刷新按钮元素
function getSpecificElement() {
    // const specificPathValue = "M5.792 2.492a4.667 4.667 0 0 1 5.065 1.881H9.043a.583.583 0 1 0 0 1.167h3.206a.584.584 0 0 0 .584-.583V1.75a.583.583 0 0 0-1.166 0V3.5a5.833 5.833 0 1 0 .385 6.417.583.583 0 1 0-1.01-.584 4.666 4.666 0 1 1-5.25-6.84Z";
    const specificPathValue = "M5.79 2.492a4.667 4.667 0 0 1 5.065 1.882H9.04a.583.583 0 0 0 0 1.166h3.206a.584.584 0 0 0 .584-.583V1.75a.583.583 0 1 0-1.167 0V3.5a5.834 5.834 0 1 0 .385 6.417.583.583 0 1 0-1.01-.584 4.666 4.666 0 1 1-5.25-6.84Z";

    const allPaths = document.querySelectorAll('path');
    for (let path of allPaths) {
        if (path.getAttribute('d') === specificPathValue) {
            return path;
        }
    }
    return null;
}

// 检查刷新元素是否出现，检查回复是否完毕
function checkReply() {
    const specifiedElement = getSpecificElement();
    if (specifiedElement) {
      console.log("检测到指定元素，等待2秒后粘贴...");
      setTimeout(() => {
        console.log("准备发送信息...");
        sendMessage();
      }, 2000);  
    }
    else {
      for(let i = 3; i > 0; i--){
        setTimeout(() => {
          console.log(i*5+"秒后继续检测...");
        }, 15000 - i*5000);
      }
      setTimeout(checkReply, 30000);
    }
}

function keyboardSend(element) {
    let event = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        view: window,
        bubbles: true,
        cancelable: true,
        ctrlKey: true  // 模拟 Ctrl 键被按下
    });
    element.dispatchEvent(event);
}



// 发送消息
function sendMessage() {
    if (index >= chunks.length) {
        return;
    }
  
    let svgElement = document.querySelector('svg path[d="M14.464 8.903a1.027 1.027 0 0 0 0-1.805L2.508.625A1.01 1.01 0 0 0 1.5.645c-.312.186-.5.516-.5.881L2.32 6.68l5.608.82c.321 0 .581.224.581.5 0 .277-.26.5-.581.5-3.161.464-5.03.736-5.607.816L1 14.473a1.021 1.021 0 0 0 1.508.903l11.956-6.473Z"]');
    let sendButton = svgElement ? svgElement.closest('button') : null;
    
    
// 新的、稳定的选择器 (推荐)
    let inputArea = document.querySelector('textarea[placeholder="Start typing a prompt"]');



    inputArea.focus();
    document.execCommand('insertText', false, chunks[index]);
    // index += 1; 
    
    checkSuccessfully(); 
    function checkSuccessfully() {
        console.log("3秒后发送消息...");
        setTimeout(() => { // 在这里添加了3秒的等待
            keyboardSend(inputArea);//发送消息
            setTimeout(() => {
                const specifiedElement = getSpecificElement();
                if (specifiedElement) {
                    console.log("消息发送失败，重试中...");
                    checkSuccessfully();
                } else {
                    console.log("消息发送成功");
                    index += 1; //移动到检查成功后，确保消息真正发送
                    if (index >= chunks.length) {
                        let currentTime = new Date();
                        console.log("所有消息已成功发送!");
                        console.log("已完成。o(*￣▽￣*)ブ~~~完成时间：" + currentTime );
                        return;
                    }
                    console.log("等待50秒...");
                    setTimeout(() => {
                        console.log("检查回复中...等待30秒...");
                        checkReply(); 
                    }, 50000); 
                }
            }, 15000); //发送后的休眠时间
        }, 3000); 
    } 
}


async function loadSRTTextFromFile(file) {
    let response = await fetch(file);
    let text = await response.text();
    return text;
}

async function main() {
    let srtText = await loadSRTTextFromFile(SRT_FILE_URL);
    let lines = srtText.split('\n\n');
    let chunk_size = 50;//分割长度
    let num_chunks = Math.ceil(lines.length / chunk_size);
    chunks = [];
    for (let i = 0; i < num_chunks; i++) {
        let startIdx = i * chunk_size;
        let endIdx = (i + 1) * chunk_size;
        let chunk = lines.slice(startIdx, endIdx).join('\n\n');
        
        chunks.push(chunk);

        console.log(`正在处理字幕块: ${i+1} / ${num_chunks}`);
        console.log(`字幕块项目起始索引: ${startIdx}`);
        console.log(`字幕块项目结束索引: ${endIdx}`);
    }
    sendMessage();
}
main(); // 开始运行
