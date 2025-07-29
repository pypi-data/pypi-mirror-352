/**
 * MCP Feedback Collector 通用JavaScript工具函数
 */

// 工具函数命名空间
const MCPUtils = {
    
    /**
     * 显示状态消息
     * @param {string} text - 消息文本
     * @param {string} type - 消息类型 (success, error, warning, info)
     * @param {number} duration - 显示时长（毫秒）
     */
    showMessage(text, type = 'info', duration = 3000) {
        // 移除现有消息
        const existingMessage = document.getElementById('statusMessage');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // 创建新消息
        const messageEl = document.createElement('div');
        messageEl.id = 'statusMessage';
        messageEl.className = `status-message ${type}`;
        messageEl.textContent = text;
        
        // 添加到页面
        document.body.appendChild(messageEl);
        
        // 显示动画
        setTimeout(() => {
            messageEl.classList.add('show');
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            messageEl.classList.remove('show');
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.remove();
                }
            }, 300);
        }, duration);
    },
    
    /**
     * 格式化文件大小
     * @param {number} bytes - 字节数
     * @returns {string} 格式化后的大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * 格式化时间戳
     * @param {string|Date} timestamp - 时间戳
     * @returns {string} 格式化后的时间
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // 小于1分钟
        if (diff < 60000) {
            return '刚刚';
        }
        
        // 小于1小时
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}分钟前`;
        }
        
        // 小于1天
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}小时前`;
        }
        
        // 超过1天，显示具体时间
        return date.toLocaleString('zh-CN', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 限制时间（毫秒）
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * 验证图片文件
     * @param {File} file - 文件对象
     * @returns {Object} 验证结果
     */
    validateImageFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        
        if (!allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: `不支持的文件格式: ${file.type}`
            };
        }
        
        if (file.size > maxSize) {
            return {
                valid: false,
                message: `文件大小超过限制: ${this.formatFileSize(file.size)} > ${this.formatFileSize(maxSize)}`
            };
        }
        
        return {
            valid: true,
            message: '验证通过'
        };
    },
    
    /**
     * 将文件转换为Base64
     * @param {File} file - 文件对象
     * @returns {Promise<string>} Base64字符串
     */
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },
    
    /**
     * 从剪贴板获取图片
     * @returns {Promise<File|null>} 图片文件或null
     */
    async getImageFromClipboard() {
        try {
            const clipboardItems = await navigator.clipboard.read();
            
            for (const clipboardItem of clipboardItems) {
                for (const type of clipboardItem.types) {
                    if (type.startsWith('image/')) {
                        const blob = await clipboardItem.getType(type);
                        return new File([blob], 'clipboard.png', { type: blob.type });
                    }
                }
            }
            
            return null;
        } catch (error) {
            console.error('无法访问剪贴板:', error);
            return null;
        }
    },
    
    /**
     * 创建模态对话框
     * @param {string} title - 标题
     * @param {string} content - 内容
     * @param {Array} buttons - 按钮配置
     * @returns {Promise} 用户选择的结果
     */
    showModal(title, content, buttons = []) {
        return new Promise((resolve) => {
            // 创建模态框
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            
            // 标题
            const header = document.createElement('div');
            header.className = 'modal-header';
            header.innerHTML = `
                <div class="modal-title">${title}</div>
                <button class="modal-close" onclick="this.closest('.modal').remove(); resolve(null);">×</button>
            `;
            
            // 内容
            const body = document.createElement('div');
            body.className = 'modal-body';
            body.innerHTML = content;
            
            // 按钮
            const footer = document.createElement('div');
            footer.className = 'modal-footer';
            
            buttons.forEach(button => {
                const btn = document.createElement('button');
                btn.className = `btn ${button.class || 'btn-secondary'}`;
                btn.textContent = button.text;
                btn.onclick = () => {
                    modal.remove();
                    resolve(button.value);
                };
                footer.appendChild(btn);
            });
            
            modalContent.appendChild(header);
            modalContent.appendChild(body);
            modalContent.appendChild(footer);
            modal.appendChild(modalContent);
            
            document.body.appendChild(modal);
            
            // 点击背景关闭
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(null);
                }
            };
        });
    },
    
    /**
     * 确认对话框
     * @param {string} message - 确认消息
     * @param {string} title - 标题
     * @returns {Promise<boolean>} 用户确认结果
     */
    confirm(message, title = '确认') {
        return this.showModal(title, message, [
            { text: '取消', class: 'btn-secondary', value: false },
            { text: '确认', class: 'btn-primary', value: true }
        ]);
    },
    
    /**
     * 复制文本到剪贴板
     * @param {string} text - 要复制的文本
     * @returns {Promise<boolean>} 复制是否成功
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('复制失败:', error);
            return false;
        }
    },
    
    /**
     * 下载文件
     * @param {string} content - 文件内容
     * @param {string} filename - 文件名
     * @param {string} mimeType - MIME类型
     */
    downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    },
    
    /**
     * 获取设备信息
     * @returns {Object} 设备信息
     */
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            screenWidth: screen.width,
            screenHeight: screen.height,
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight
        };
    }
};

// 全局快捷键处理
document.addEventListener('keydown', (e) => {
    // Ctrl+/ 显示快捷键帮助
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        MCPUtils.showModal('快捷键帮助', `
            <div style="text-align: left;">
                <p><kbd>Ctrl+V</kbd> - 粘贴图片</p>
                <p><kbd>Enter</kbd> - 发送消息</p>
                <p><kbd>Ctrl+Enter</kbd> - 提交反馈</p>
                <p><kbd>Esc</kbd> - 取消操作</p>
                <p><kbd>Ctrl+/</kbd> - 显示此帮助</p>
            </div>
        `, [
            { text: '关闭', class: 'btn-primary', value: true }
        ]);
    }
});

// 导出到全局
window.MCPUtils = MCPUtils;
