// 全局变量
let ws = null;
let isTeacher = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

// DOM元素
const teacherModeBtn = document.getElementById('teacherModeBtn');
const logoutBtn = document.getElementById('logoutBtn');
const passwordModal = document.getElementById('passwordModal');
const passwordInput = document.getElementById('passwordInput');
const loginBtn = document.getElementById('loginBtn');
const cancelBtn = document.getElementById('cancelBtn');
const startBroadcastBtn = document.getElementById('startBroadcastBtn');
const stopBroadcastBtn = document.getElementById('stopBroadcastBtn');
const screenSourceBtn = document.getElementById('screenSourceBtn');
const cameraSourceBtn = document.getElementById('cameraSourceBtn');
const broadcastImage = document.getElementById('broadcastImage');
const broadcastStatus = document.querySelector('.broadcast-status');
const broadcastControls = document.querySelector('.broadcast-controls');
const fileControls = document.querySelector('.file-controls');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const viewAssignmentsBtn = document.getElementById('viewAssignmentsBtn');
const fileTable = document.getElementById('fileTable').querySelector('tbody');
const transferFileInput = document.getElementById('transferFileInput');
const transferUploadBtn = document.getElementById('transferUploadBtn');
const transferFileTable = document.getElementById('transferFileTable').querySelector('tbody');
const assignmentFileInput = document.getElementById('assignmentFileInput');
const submitAssignmentBtn = document.getElementById('submitAssignmentBtn');
const studentControls = document.querySelector('.student-controls');

// 广播数据包管理
let broadcastPackages = [];

// 工具函数
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

function showElement(element) {
    element.style.display = '';
}

function hideElement(element) {
    element.style.display = 'none';
}

function toggleElement(element) {
    element.style.display = element.style.display === 'none' ? '' : 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 广播历史记录
let broadcastHistory = [];

// 加载广播数据包列表
async function loadBroadcastPackages() {
    try {
        const response = await fetch('/api/broadcast_packages');
        broadcastPackages = await response.json();
        updatePackageList();
    } catch (error) {
        console.error('加载广播数据包列表错误:', error);
    }
}

// 更新广播数据包列表
function updatePackageList() {
    const packageList = document.getElementById('packageList');
    packageList.innerHTML = '';
    
    console.log('更新广播包列表，教师状态:', isTeacher);  // 添加调试日志
    
    broadcastPackages.forEach(package => {
        const div = document.createElement('div');
        div.className = 'package-item';
        div.innerHTML = `
            <div class="package-info">
                <span class="package-name">${package.name}</span>
                <span class="package-time">${new Date(package.timestamp).toLocaleString()}</span>
            </div>
            <div class="package-actions">
                ${isTeacher ? `
                    <button class="btn" onclick="renamePackage('${package.id}')">重命名</button>
                    <button class="btn danger" onclick="deletePackage('${package.id}')">删除</button>
                ` : `
                    <button class="btn" onclick="loadPackage('${package.id}')">查看</button>
                `}
            </div>
        `;
        packageList.appendChild(div);
    });
}

// 加载广播数据包
async function loadPackage(packageId) {
    try {
        const response = await fetch(`/api/broadcast_package/${packageId}`);
        const package = await response.json();
        
        // 更新历史记录
        broadcastHistory = package.frames;
        updateHistorySlider();
        
        // 显示第一帧
        if (broadcastHistory.length > 0) {
            const firstFrame = broadcastHistory[0];
            broadcastImage.src = `data:image/jpeg;base64,${firstFrame.image}`;
            showElement(broadcastImage);
            
            const date = new Date(firstFrame.timestamp);
            document.getElementById('historyTime').textContent = date.toLocaleTimeString();
            
            // 显示学生控制界面
            showElement(studentControls);
            hideElement(broadcastControls);
        }
    } catch (error) {
        console.error('加载广播数据包错误:', error);
        alert('加载失败，请重试');
    }
}

// 重命名广播数据包
async function renamePackage(packageId) {
    if (!isTeacher) {
        alert('无权限重命名广播数据包');
        return;
    }
    
    const package = broadcastPackages.find(p => p.id === packageId);
    if (!package) return;
    
    const newName = prompt('请输入新的名称:', package.name);
    if (!newName || newName === package.name) return;
    
    try {
        ws.send(JSON.stringify({
            type: 'rename_package',
            package_id: packageId,
            new_name: newName
        }));
    } catch (error) {
        console.error('重命名广播数据包错误:', error);
        alert('重命名失败，请重试');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 教师模式开关
    teacherModeBtn.addEventListener('click', showPasswordModal);
    logoutBtn.addEventListener('click', logout);
    
    // 登录
    loginBtn.addEventListener('click', login);
    cancelBtn.addEventListener('click', hidePasswordModal);
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') login();
    });
    
    // 广播控制
    startBroadcastBtn.addEventListener('click', startBroadcast);
    stopBroadcastBtn.addEventListener('click', stopBroadcast);
    screenSourceBtn.addEventListener('click', () => switchSource(false));
    cameraSourceBtn.addEventListener('click', () => switchSource(true));
    
    // 文件上传 - 使用一次性事件监听器
    uploadBtn.onclick = () => fileInput.click();
    fileInput.onchange = uploadFile;

    // 作业相关
    viewAssignmentsBtn.addEventListener('click', viewAssignments);
    transferUploadBtn.onclick = () => transferFileInput.click();
    transferFileInput.onchange = uploadTransferFile;
    submitAssignmentBtn.onclick = () => assignmentFileInput.click();
    assignmentFileInput.onchange = submitAssignment;

    // 历史记录滑块
    const historySlider = document.getElementById('historySlider');
    historySlider.addEventListener('input', () => {
        const index = parseInt(historySlider.value);
        if (index >= 0 && index < broadcastHistory.length) {
            const frame = broadcastHistory[index];
            broadcastImage.src = `data:image/jpeg;base64,${frame.image}`;
            showElement(broadcastImage);
            
            const date = new Date(frame.timestamp);
            document.getElementById('historyTime').textContent = date.toLocaleTimeString();
        }
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    connectWebSocket();
    loadFiles();
    loadTransferFiles();
    loadAssignments();
    loadBroadcastPackages();
});

// WebSocket连接
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:${parseInt(window.location.port) + 1}`;
    
    console.log('正在连接WebSocket:', wsUrl);
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket连接已建立');
        reconnectAttempts = 0;
    };
    
    ws.onclose = () => {
        console.log('WebSocket连接已关闭');
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            console.log(`尝试重新连接 (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
            setTimeout(connectWebSocket, RECONNECT_DELAY);
            reconnectAttempts++;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            console.error('处理WebSocket消息错误:', error);
        }
    };
}

// 显示密码输入对话框
function showPasswordModal() {
    passwordModal.classList.add('show');
    passwordInput.focus();
}

// 关闭密码输入对话框
function hidePasswordModal() {
    passwordModal.classList.remove('show');
    passwordInput.value = '';
}

// 教师登录
async function login() {
    const password = passwordInput.value;
    if (!password) return;
    
    try {
        // 通过 WebSocket 发送登录请求
        ws.send(JSON.stringify({
            type: 'teacher_login',
            password: password
        }));
    } catch (error) {
        console.error('登录错误:', error);
        alert('登录失败，请重试');
    }
}

// 教师登出
async function logout() {
    try {
        // 通过 WebSocket 发送登出请求
        ws.send(JSON.stringify({
            type: 'teacher_logout'
        }));
    } catch (error) {
        console.error('登出错误:', error);
    }
}

// 更新教师界面
function updateTeacherUI(isTeacher) {
    if (isTeacher) {
        hideElement(teacherModeBtn);
        showElement(logoutBtn);
        showElement(broadcastControls);
        hideElement(studentControls);
        showElement(fileControls);
        console.log('切换到教师界面');
        } else {
        showElement(teacherModeBtn);
        hideElement(logoutBtn);
        hideElement(broadcastControls);
        showElement(studentControls);
        hideElement(fileControls);
        console.log('切换到学生界面');
    }
}

// 加载文件列表
async function loadFiles() {
    try {
        const response = await fetch('/api/files');
        const files = await response.json();
        
        fileTable.innerHTML = '';
        files.forEach(file => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${file.name}</td>
                <td>${formatFileSize(file.size)}</td>
                <td>${file.upload_time}</td>
                <td>
                    <button class="btn" onclick="downloadFile('${file.name}')">下载</button>
                    <button class="btn danger" onclick="deleteFile('${file.name}')">删除</button>
                </td>
            `;
            fileTable.appendChild(tr);
        });
    } catch (error) {
        console.error('加载文件列表错误:', error);
    }
}

async function loadTransferFiles() {
    try {
        const response = await fetch('/api/transfer_files');
        const files = await response.json();
        
        transferFileTable.innerHTML = '';
        files.forEach(file => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${file.name}</td>
                <td>${formatFileSize(file.size)}</td>
                <td>${file.upload_time}</td>
                <td>
                    <button class="btn" onclick="downloadTransferFile('${file.name}')">下载</button>
                    <button class="btn danger" onclick="deleteTransferFile('${file.name}')">删除</button>
                </td>
            `;
            transferFileTable.appendChild(tr);
        });
    } catch (error) {
        console.error('加载中转站文件列表错误:', error);
    }
}

// 上传文件
async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
        method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        if (data.success) {
            fileInput.value = '';
            loadFiles();
        } else {
            alert(data.error || '上传失败');
        }
    } catch (error) {
        console.error('上传文件错误:', error);
        alert('上传失败，请重试');
    }
}

async function uploadTransferFile() {
    const file = transferFileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'transfer');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        if (data.success) {
            transferFileInput.value = '';
            loadTransferFiles();
        } else {
            alert(data.error || '上传失败');
        }
    } catch (error) {
        console.error('上传文件错误:', error);
        alert('上传失败，请重试');
    }
}

async function submitAssignment() {
    const file = assignmentFileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'assignment');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        if (data.success) {
            assignmentFileInput.value = '';
            alert('作业提交成功');
        } else {
            alert(data.error || '提交失败');
        }
    } catch (error) {
        console.error('提交作业错误:', error);
        alert('提交失败，请重试');
    }
}

// 下载文件
function downloadFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}`;
}

function downloadTransferFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}?type=transfer`;
}

// 删除文件
async function deleteFile(filename) {
    if (!confirm('确定要删除这个文件吗？')) return;
    
    try {
        const response = await fetch(`/delete/${encodeURIComponent(filename)}`);
        const data = await response.json();
            if (data.success) {
                loadFiles();
            } else {
                alert(data.error || '删除失败');
            }
    } catch (error) {
        console.error('删除文件错误:', error);
        alert('删除失败，请重试');
    }
}

// 删除中转站文件
async function deleteTransferFile(filename) {
    if (!confirm('确定要删除这个文件吗？')) return;
    
    try {
        const response = await fetch(`/delete_file/${encodeURIComponent(filename)}?type=transfer`);
        const data = await response.json();
        if (data.message) {
            loadTransferFiles();
        } else {
            alert(data.error || '删除失败');
        }
    } catch (error) {
        console.error('删除文件错误:', error);
        alert('删除失败，请重试');
    }
}

// 切换视频源
function switchSource(useCamera) {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    
    // 如果尝试使用摄像头但按钮被禁用，直接返回
    if (useCamera && cameraSourceBtn.disabled) {
        return;
    }
    
    // 更新按钮状态
    if (useCamera) {
        screenSourceBtn.classList.remove('active');
        cameraSourceBtn.classList.add('active');
    } else {
        screenSourceBtn.classList.add('active');
        cameraSourceBtn.classList.remove('active');
    }
    
    console.log('切换视频源:', useCamera ? '摄像头' : '屏幕');
    ws.send(JSON.stringify({ type: 'switch_source', use_camera: useCamera }));
}

// 开始广播
function startBroadcast() {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    
    // 清空历史记录
    broadcastHistory = [];
    updateHistorySlider();
    
    console.log('开始广播');
    ws.send(JSON.stringify({ type: 'start_broadcast' }));
}

// 停止广播
function stopBroadcast() {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    console.log('停止广播');
    ws.send(JSON.stringify({ type: 'stop_broadcast' }));
}

// 更新广播状态
function updateBroadcastStatus(status) {
    if (status === 'started') {
        showElement(stopBroadcastBtn);
        hideElement(startBroadcastBtn);
        broadcastStatus.textContent = '正在广播';
        broadcastStatus.classList.add('active');
        // 默认选择屏幕
        screenSourceBtn.classList.add('active');
        cameraSourceBtn.classList.remove('active');
    } else {
        showElement(startBroadcastBtn);
        hideElement(stopBroadcastBtn);
        broadcastStatus.textContent = '未开始广播';
        broadcastStatus.classList.remove('active');
        hideElement(broadcastImage);
    }
}

// 更新历史记录滑块
function updateHistorySlider() {
    const slider = document.getElementById('historySlider');
    const timeDisplay = document.getElementById('historyTime');
    
    slider.max = broadcastHistory.length - 1;
    if (broadcastHistory.length > 0) {
        const currentFrame = broadcastHistory[slider.value];
        const date = new Date(currentFrame.timestamp);
        timeDisplay.textContent = date.toLocaleTimeString();
    }
}

function viewAssignments() {
    window.location.href = '/assignments';
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'login_result':
            if (data.success) {
                hidePasswordModal();
                isTeacher = true;
                updateTeacherUI(true);
                console.log('教师登录成功');
                loadBroadcastPackages();
            } else {
                alert(data.message || '登录失败');
            }
            break;
        case 'logout_result':
            if (data.success) {
                isTeacher = false;
                updateTeacherUI(false);
                loadBroadcastPackages();
            }
            break;
        case 'broadcast_status':
            updateBroadcastStatus(data.status);
            if (data.has_camera === false) {
                cameraSourceBtn.disabled = true;
                cameraSourceBtn.title = '摄像头不可用';
            }
            break;
        case 'image':
            broadcastImage.src = `data:image/jpeg;base64,${data.image}`;
            showElement(broadcastImage);
            broadcastStatus.textContent = '正在广播';
            broadcastStatus.classList.add('active');
            if (isTeacher) {
                broadcastHistory.push({
                    timestamp: data.timestamp,
                    image: data.image
                });
                if (broadcastHistory.length > 1000) {
                    broadcastHistory.shift();
                }
                updateHistorySlider();
            }
            break;
        case 'packages_list':
            broadcastPackages = data.packages;
            updatePackageList();
            break;
        case 'package_deleted':
            broadcastPackages = broadcastPackages.filter(p => p.id !== data.package_id);
            updatePackageList();
            break;
        case 'error':
            alert(data.message);
            break;
    }
}

// 删除广播数据包
async function deletePackage(packageId) {
    if (!isTeacher) {
        alert('无权限删除广播数据包');
        return;
    }
    
    if (!confirm('确定要删除这个广播数据包吗？')) {
        return;
    }
    
    try {
        ws.send(JSON.stringify({
            type: 'delete_package',
            package_id: packageId
        }));
    } catch (error) {
        console.error('删除广播数据包错误:', error);
        alert('删除失败，请重试');
    }
} 