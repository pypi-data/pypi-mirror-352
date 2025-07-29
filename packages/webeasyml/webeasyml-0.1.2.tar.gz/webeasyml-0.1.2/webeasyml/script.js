// 主构造参数配置
const mainArgsMap = {
    classification: {
        KNN: ['n_neighbors'],
        SVM: [],
        NaiveBayes: [],
        CART: [],
        AdaBoost: ['n_estimators', 'learning_rate'],
        MLP: ['hidden_layer_sizes', 'solver', 'learning_rate_init', 'max_iter'],
        RandomForest: ['n_estimators']
    },
    regression: {
        LinearRegression: [],
        CART: [],
        RandomForest: ['n_estimators'],
        Polynomial: ['degree'],
        Lasso: ['alpha'],
        Ridge: ['alpha'],
        SVM: ['kernel', 'degree'],
        AdaBoost: ['n_estimators', 'learning_rate'],
        MLP: ['hidden_layer_sizes', 'solver', 'learning_rate_init', 'max_iter']
    },
    clustering: {
        Kmeans: ['n_clusters'],
        'Spectral clustering': ['n_clusters'],
        'Agglomerative clustering': ['n_clusters'],
        Birch: ['n_clusters']
    },
    dimension: {
        PCA: ['n_components'],
        LDA: ['n_components'],
        LLE: ['n_components']
    }
};

// 模型配置
const modelConfigs = {
    classification: {
        name: '分类模型',
        algorithms: ['KNN', 'SVM', 'NaiveBayes', 'CART', 'AdaBoost', 'MLP', 'RandomForest'],
        defaultParams: {
            KNN: { n_neighbors: 5 },
            SVM: { kernel: 'rbf', degree: 3 },
            NaiveBayes: {},
            CART: { max_depth: 3 },
            AdaBoost: { n_estimators: 100, learning_rate: 1.0 },
            MLP: { hidden_layer_sizes: '(100,)', solver: 'lbfgs', learning_rate_init: 0.001, max_iter: 200 },
            RandomForest: { n_estimators: 100, max_depth: null }
        }
    },
    regression: {
        name: '回归模型',
        algorithms: ['LinearRegression', 'CART', 'RandomForest', 'Polynomial', 'Lasso', 'Ridge', 'SVM', 'AdaBoost', 'MLP'],
        defaultParams: {
            LinearRegression: {},
            CART: { max_depth: 3 },
            RandomForest: { n_estimators: 20, max_depth: null },
            Polynomial: { degree: 2 },
            Lasso: { alpha: 1.0 },
            Ridge: { alpha: 1.0 },
            SVM: { kernel: 'rbf', degree: 3 },
            AdaBoost: { n_estimators: 100, learning_rate: 1.0 },
            MLP: { hidden_layer_sizes: '(100,)', solver: 'lbfgs', learning_rate_init: 0.001, max_iter: 200 }
        }
    },
    clustering: {
        name: '聚类模型',
        algorithms: ['Kmeans', 'Spectral clustering', 'Agglomerative clustering', 'Birch'],
        defaultParams: {
            Kmeans: { n_clusters: 5 },
            'Spectral clustering': { n_clusters: 5 },
            'Agglomerative clustering': { n_clusters: 5 },
            Birch: { n_clusters: 5 }
        }
    },
    dimension: {
        name: '降维模型',
        algorithms: ['PCA', 'LDA', 'LLE'],
        defaultParams: {
            PCA: { n_components: 2 },
            LDA: { n_components: 2 },
            LLE: { n_components: 2 }
        }
    }
};

let currentModelType = null;
let currentAlgorithm = null;
let uploadedDatasetName = '';
let uploadedColCount = 0;
let uploadedColNames = [];

// 工具函数
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }, 100);
};

// 选择模型类型
function selectModel(type) {
    currentModelType = type;
    const config = modelConfigs[type];
    // 更新按钮状态
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('onclick').includes(type)) {
            btn.classList.add('active');
        }
    });
    // 动态生成算法按钮组
    const algorithmBtnGroup = document.getElementById('algorithmBtnGroup');
    algorithmBtnGroup.innerHTML = config.algorithms.map(alg => `
        <button type="button" class="btn btn-outline-primary me-2" onclick="selectAlgorithm('${alg}')">${alg}</button>
    `).join('');
    // 清空参数区
    document.getElementById('paramsContainer').innerHTML = '';
    document.getElementById('paramsCollapse').style.display = 'none';
}

function selectAlgorithm(algorithm) {
    currentAlgorithm = algorithm;
    // 高亮当前算法按钮
    document.querySelectorAll('#algorithmBtnGroup .btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === algorithm) btn.classList.add('active');
    });
    // 切换算法时参数区保持收起，按钮文字为"更多参数"
    const paramsCollapse = document.getElementById('paramsCollapse');
    const toggleBtn = document.getElementById('toggleParamsBtn');
    if (paramsCollapse) paramsCollapse.style.display = 'none';
    if (toggleBtn) toggleBtn.textContent = '更多参数';
    updateParams();
}

function toggleParams() {
    const collapse = document.getElementById('paramsCollapse');
    const btn = document.getElementById('toggleParamsBtn');
    if (!collapse || !btn) return;
    if (collapse.style.display === 'none' || collapse.style.display === '') {
        collapse.style.display = '';
        btn.textContent = '收起参数';
    } else {
        collapse.style.display = 'none';
        btn.textContent = '更多参数';
    }
}

function updateParams() {
    if (!currentAlgorithm) return;
    const params = modelConfigs[currentModelType].defaultParams[currentAlgorithm];
    const paramsContainer = document.getElementById('paramsContainer');
    paramsContainer.innerHTML = '';
    let paramsHtml = '';
    if (params && Object.keys(params).length > 0) {
        paramsHtml = Object.entries(params).map(([key, value]) => `
            <div class=\"mb-3\">
                <label class=\"form-label\">${key}</label>
                <input type=\"text\" class=\"form-control\" id=\"param_${key}\" value=\"${value === null ? '' : value}\" data-default=\"${value === null ? '' : value}\"> 
            </div>
        `).join('');
    } else {
        paramsHtml = '<div class="mb-3" style="color:#888;">无可选参数</div>';
    }
    paramsContainer.innerHTML = paramsHtml;
    // 添加动画效果
    const newParams = paramsContainer.querySelectorAll('.mb-3');
    newParams.forEach((param, index) => {
        param.style.opacity = '0';
        param.style.transform = 'translateY(10px)';
        setTimeout(() => {
            param.style.opacity = '1';
            param.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function isValidPyVarName(name) {
    // 不能是关键字，不能以数字开头，只能字母数字下划线
    return /^[_a-zA-Z][_a-zA-Z0-9]*$/.test(name) && !['False','None','True','and','as','assert','break','class','continue','def','del','elif','else','except','finally','for','from','global','if','import','in','is','lambda','nonlocal','not','or','pass','raise','return','try','while','with','yield'].includes(name);
}

// 生成代码
function generateCode() {
    // 恢复用户自选模型名称
    const modelNameInput = document.getElementById('modelName').value.trim();
    const modelName = modelNameInput || 'my_model';
    if (!isValidPyVarName(modelName)) {
        showToast('模型名称不合法，只能用字母、数字、下划线，且不能以数字开头', 'error');
        return;
    }
    // 获取当前算法
    let algorithm = currentAlgorithm;
    if (!algorithm) {
        showToast('请先选择算法', 'error');
        return;
    }
    // 参数分拣
    let mainParams = [];
    let paraParams = {};
    let setParaParams = {};
    const mainArgs = (mainArgsMap[currentModelType] && mainArgsMap[currentModelType][algorithm]) || [];
    // 只有参数区展开时才收集参数
    const paramsCollapse = document.getElementById('paramsCollapse');
    let addSetPara = paramsCollapse && paramsCollapse.style.display !== 'none';
    if (addSetPara) {
        const paramInputs = document.querySelectorAll('[id^="param_"]');
        paramInputs.forEach(input => {
            const paramName = input.id.replace('param_', '');
            const value = input.value;
            const defaultValue = input.getAttribute('data-default');
            if (mainArgs.includes(paramName)) {
                mainParams.push(`${paramName}=${value}`);
            } else {
                // 只有用户修改了默认值才加入set_para
                if (value !== defaultValue) {
                    setParaParams[paramName] = value;
                }
            }
        });
    }
    // para参数格式：para={'key':value,...}，字符串加引号
    let paraStr = '';
    if (Object.keys(paraParams).length > 0) {
        const paraDict = Object.entries(paraParams).map(([k, v]) => {
            if (!isNaN(v) && v !== '') return `'${k}':${v}`;
            if (v === 'True' || v === 'False') return `'${k}':${v}`;
            return `'${k}':'${v}'`;
        }).join(', ');
        paraStr = `para={${paraDict}}`;
    }
    let allArgs = [
        `'${algorithm}'`,
        ...mainParams,
        paraStr
    ].filter(Boolean).join(', ');
    // 生成代码
    let code = '';
    code += `from BaseML import ${currentModelType === 'classification' ? 'Classification' : 
        currentModelType === 'regression' ? 'Regression' :
        currentModelType === 'clustering' ? 'Cluster' : 'DimentionReduction'}\n\n`;
    code += `# 创建模型实例\n`;
    code += `${modelName} = ${currentModelType === 'classification' ? 'Classification' : 
        currentModelType === 'regression' ? 'Regression' :
        currentModelType === 'clustering' ? 'Cluster' : 'DimentionReduction'}(${allArgs})\n\n`;
    code += `# 加载数据\n`;
    let datasetName = 'your_data.csv';
    if (uploadedDatasetName && uploadedDatasetName.trim() !== '') {
        datasetName = uploadedDatasetName;
    }
    code += `${modelName}.load_tab_data('${datasetName}')\n\n`;
    // 只有参数区展开且有set_para参数时才添加set_para
    if (addSetPara && Object.keys(setParaParams).length > 0) {
        const setParaStr = Object.entries(setParaParams).map(([k, v]) => {
            if (!isNaN(v) && v !== '') return `${k}=${v}`;
            if (v === 'True' || v === 'False') return `${k}=${v}`;
            return `${k}='${v}'`;
        }).join(', ');
        code += `${modelName}.set_para(${setParaStr})\n\n`;
    }
    code += `# 训练模型\n`;
    code += `${modelName}.train()\n\n`;
    code += `# 保存模型\n`;
    code += `${modelName}.save('${modelName}.pkl')\n`;
    const codeOutput = document.getElementById('codeOutput');
    codeOutput.textContent = code;
    // 添加动画效果
    codeOutput.style.opacity = '0';
    setTimeout(() => {
        codeOutput.style.opacity = '1';
    }, 50);
    showToast('代码生成成功！', 'success');
}

// 复制代码
function copyCode() {
    const code = document.getElementById('codeOutput').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showToast('代码已复制到剪贴板！', 'success');
    }).catch(() => {
        showToast('复制失败，请手动复制', 'error');
    });
}

// 运行代码
async function runCode() {
    const code = document.getElementById('codeOutput').textContent;
    if (!code) {
        showToast('请先生成代码！', 'error');
        return;
    }

    // 显示加载状态
    const runButton = document.querySelector('button[onclick="runCode()"]');
    const originalText = runButton.textContent;
    runButton.disabled = true;
    runButton.textContent = '训练中...';

    try {
        const response = await fetch('/run_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });

        const result = await response.json();
        
        if (result.success) {
            showToast('代码运行成功！模型已生成，点击下方按钮下载。', 'success');
            document.getElementById('downloadModelBtn').style.display = '';
            // 使用更友好的方式显示输出
            const outputLines = result.output.split('\n').filter(line => line.trim());
            if (outputLines.length > 0) {
                alert('训练输出：\n' + outputLines.join('\n'));
            }
        } else {
            showToast('代码运行失败！', 'error');
            document.getElementById('downloadModelBtn').style.display = 'none';
            // 格式化错误信息显示
            const errorLines = result.error.split('\n').filter(line => line.trim());
            const formattedError = errorLines.map(line => {
                if (line.includes('Error:') || line.includes('错误:')) {
                    return '\n' + line;
                }
                return line;
            }).join('\n');
            alert('训练失败：\n' + formattedError);
        }
    } catch (error) {
        showToast('运行代码时发生错误：' + error.message, 'error');
        document.getElementById('downloadModelBtn').style.display = 'none';
        alert('系统错误：\n' + error.message);
    } finally {
        // 恢复按钮状态
        runButton.disabled = false;
        runButton.textContent = originalText;
    }
}

// 下载模型
async function downloadModel() {
    const modelName = document.getElementById('modelName').value || 'my_model';
    
    try {
        const response = await fetch(`/download_model?model_name=${modelName}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${modelName}.pkl`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            showToast('模型下载成功！', 'success');
        } else {
            const error = await response.json();
            showToast('下载模型失败：' + error.error, 'error');
        }
    } catch (error) {
        showToast('下载模型时发生错误：' + error.message, 'error');
    }
}

// 上传数据集
function uploadDataset() {
    const fileInput = document.getElementById('datasetFile');
    if (!fileInput.files.length) {
        showToast('请先选择一个CSV文件', 'error');
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_dataset', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            uploadedDatasetName = data.filename;
            uploadedColCount = data.col_count || 0;
            uploadedColNames = data.col_names || [];
            document.getElementById('datasetFileName').textContent = '已上传：' + data.filename + (uploadedColCount ? `（${uploadedColCount}列）` : '');
            showToast('数据集上传成功！', 'success');
            console.log('上传数据集列数:', uploadedColCount, '列名:', uploadedColNames);
        } else {
            showToast('上传失败：' + data.error, 'error');
        }
    })
    .catch(err => {
        showToast('上传失败：' + err.message, 'error');
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 添加CSS动画样式
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 4px;
            color: white;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        .toast-info { background-color: #3498db; }
        .toast-success { background-color: #2ecc71; }
        .toast-error { background-color: #e74c3c; }
        
        .btn.active {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .form-select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: var(--border-radius);
            margin-bottom: 1rem;
            transition: var(--transition);
        }
        
        .form-select:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }
        
        #paramsContainer > div {
            transition: all 0.3s ease;
        }
        
        #codeOutput {
            transition: opacity 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    // 自动上传数据集
    const fileInput = document.getElementById('datasetFile');
    const datasetFileNameDiv = document.getElementById('datasetFileName');
    const defaultDatasetHint = document.getElementById('defaultDatasetHint');

    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                uploadDataset();
                datasetFileNameDiv.style.display = '';
                defaultDatasetHint.style.display = 'none';
            } else {
                datasetFileNameDiv.textContent = '';
                datasetFileNameDiv.style.display = 'none';
                defaultDatasetHint.style.display = '';
            }
        });

        if (fileInput.files.length === 0) {
             defaultDatasetHint.style.display = '';
             datasetFileNameDiv.style.display = 'none';
        } else {
             defaultDatasetHint.style.display = 'none';
        }
    }

    // 默认选择分类模型和KNN算法
    selectModel('classification');
    selectAlgorithm('KNN');
}); 