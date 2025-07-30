// 全局变量
let isSubmitting = false;

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    loadCurrentConfig();
    loadServerPath();
});

// 加载服务器路径信息
async function loadServerPath() {
    try {
        const response = await fetch('/api/server-path');
        const data = await response.json();
        
        if (data.success) {
            const serverPathInfo = document.getElementById('serverPathInfo');
            const serverPathDisplay = document.getElementById('serverPathDisplay');
            
            if (serverPathInfo && serverPathDisplay) {
                serverPathDisplay.textContent = data.server_path;
                serverPathInfo.style.display = 'block';
                
                // 如果是EXE文件，添加特殊标识
                if (data.is_exe) {
                    serverPathDisplay.innerHTML = `<i class="fas fa-file-code" style="color: #4caf50; margin-right: 8px;"></i>${data.server_path}`;
                }
            }
        }
    } catch (error) {
        console.error('加载服务器路径失败:', error);
    }
}

// 初始化表单
function initializeForm() {
    const form = document.getElementById('configForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // 添加输入验证
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('input', validateInput);
        input.addEventListener('blur', validateInput);
    });
}

// 加载当前配置
async function loadCurrentConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success) {
            populateForm(data.config);
        } else {
            showStatus('error', '加载失败', data.error);
        }
    } catch (error) {
        console.error('加载配置失败:', error);
        showStatus('error', '加载失败', '无法连接到服务器');
    }
}

// 填充表单数据
function populateForm(config) {
    document.getElementById('mc_host').value = config.MC_HOST || 'localhost';
    document.getElementById('mc_port').value = config.MC_RCON_PORT || '25575';
    document.getElementById('mc_password').value = config.MC_RCON_PASSWORD || '';
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isSubmitting) return;
    
    const formData = new FormData(event.target);
    const config = {
        MC_HOST: formData.get('MC_HOST') || 'localhost',
        MC_RCON_PORT: formData.get('MC_RCON_PORT') || '25575',
        MC_RCON_PASSWORD: formData.get('MC_RCON_PASSWORD')
    };
    
    // 验证表单
    if (!validateForm(config)) {
        return;
    }
    
    isSubmitting = true;
    showStatus('info', '保存中...', '正在保存配置，请稍候');
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('success', '保存成功', data.message);
            // 3秒后隐藏状态卡片
            setTimeout(() => {
                hideStatus();
            }, 3000);
        } else {
            showStatus('error', '保存失败', data.error);
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        showStatus('error', '保存失败', '无法连接到服务器');
    } finally {
        isSubmitting = false;
    }
}

// 测试连接
async function testConnection() {
    const config = {
        MC_HOST: document.getElementById('mc_host').value || 'localhost',
        MC_RCON_PORT: document.getElementById('mc_port').value || '25575',
        MC_RCON_PASSWORD: document.getElementById('mc_password').value
    };
    
    if (!config.MC_RCON_PASSWORD) {
        showStatus('error', '测试失败', 'RCON密码不能为空');
        return;
    }
    
    showStatus('info', '测试连接中...', '正在尝试连接到Minecraft服务器');
    
    try {
        // 先保存配置
        const saveResponse = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!saveResponse.ok) {
            throw new Error('保存配置失败');
        }
        
        // 然后测试连接
        const testResponse = await fetch('/api/test-connection', {
            method: 'POST'
        });
        
        const data = await testResponse.json();
        
        if (data.success) {
            showStatus('success', '连接成功', `服务器响应: ${data.server_response}`);
        } else {
            showStatus('error', '连接失败', data.error);
        }
    } catch (error) {
        console.error('测试连接失败:', error);
        showStatus('error', '连接失败', '无法连接到服务器');
    }
}

// 表单验证
function validateForm(config) {
    const errors = [];
    
    if (!config.MC_RCON_PASSWORD) {
        errors.push('RCON密码不能为空');
    }
    
    const port = parseInt(config.MC_RCON_PORT);
    if (isNaN(port) || port < 1 || port > 65535) {
        errors.push('端口号必须是1-65535之间的数字');
    }
    
    if (errors.length > 0) {
        showStatus('error', '验证失败', errors.join('\n'));
        return false;
    }
    
    return true;
}

// 输入验证
function validateInput(event) {
    const input = event.target;
    const value = input.value;
    
    // 移除之前的错误状态
    input.classList.remove('error');
    
    // 验证规则
    if (input.name === 'MC_RCON_PORT') {
        const port = parseInt(value);
        if (value && (isNaN(port) || port < 1 || port > 65535)) {
            input.classList.add('error');
        }
    }
    
    if (input.name === 'MC_RCON_PASSWORD' && input.hasAttribute('required')) {
        if (!value.trim()) {
            input.classList.add('error');
        }
    }
}

// 显示状态信息
function showStatus(type, title, message) {
    const statusCard = document.getElementById('statusCard');
    const statusIcon = document.getElementById('statusIcon');
    const statusTitle = document.getElementById('statusTitle');
    const statusMessage = document.getElementById('statusMessage');
    
    // 清除之前的状态类
    statusIcon.className = 'fas';
    
    // 设置图标和样式
    switch (type) {
        case 'success':
            statusIcon.className = 'fas fa-check-circle';
            statusIcon.parentElement.className = 'status-icon success';
            break;
        case 'error':
            statusIcon.className = 'fas fa-exclamation-circle';
            statusIcon.parentElement.className = 'status-icon error';
            break;
        case 'info':
        default:
            statusIcon.className = 'fas fa-circle-notch fa-spin';
            statusIcon.parentElement.className = 'status-icon info';
            break;
    }
    
    // 设置文本内容
    statusTitle.textContent = title;
    statusMessage.textContent = message;
    
    // 显示状态卡片
    statusCard.style.display = 'block';
    statusCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 隐藏状态信息
function hideStatus() {
    const statusCard = document.getElementById('statusCard');
    statusCard.style.display = 'none';
}

// 切换密码显示/隐藏
function togglePassword() {
    const passwordInput = document.getElementById('mc_password');
    const passwordIcon = document.getElementById('passwordIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        passwordIcon.className = 'fas fa-eye';
    }
}

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 添加CSS错误样式
const style = document.createElement('style');
style.textContent = `
    .form-input.error {
        border-color: #e74c3c !important;
        background-color: #fdf2f2 !important;
    }
    
    .form-input.error:focus {
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important;
    }
`;
document.head.appendChild(style);