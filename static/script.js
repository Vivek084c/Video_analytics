/* ====================================
   Global State & DOM Elements
   ==================================== */

const tabs = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const modal = document.getElementById('videoModal');
const videoPlayer = document.getElementById('videoPlayer');
const closeBtn = document.querySelector('.close');
const loadingIndicator = document.getElementById('loadingIndicator');

/* ====================================
   Tab Navigation
   ==================================== */

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        tab.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    });
});

/* ====================================
   Loading Indicator Functions
   ==================================== */

function showLoading() {
    loadingIndicator.classList.add('show');
}

function hideLoading() {
    loadingIndicator.classList.remove('show');
}

/* ====================================
   Result Display Functions
   ==================================== */

function showResult(resultElementId, content) {
    const resultElement = document.getElementById(resultElementId);
    resultElement.innerHTML = content;
    resultElement.classList.add('show');
}

function clearResult(resultElementId) {
    const resultElement = document.getElementById(resultElementId);
    resultElement.innerHTML = '';
    resultElement.classList.remove('show');
}

function formatError(message) {
    return `<div class="error-message">❌ Error: ${message}</div>`;
}

function formatSuccess(message) {
    return `<div class="success-message">✓ ${message}</div>`;
}

function formatInfo(message) {
    return `<div class="info-message">ℹ ${message}</div>`;
}

/* ====================================
   API Call Wrapper
   ==================================== */

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        showLoading();
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        hideLoading();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        hideLoading();
        throw error;
    }
}

/* ====================================
   Objects Tab - API Handlers
   ==================================== */

document.getElementById('btnWhere')?.addEventListener('click', async () => {
    const objectId = document.getElementById('objectId').value.trim();
    
    if (!objectId) {
        showResult('objectResult', formatError('Please enter an Object ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/where?object_id=${objectId}`);
        
        let html = `<h3>Object ${objectId} Appearances</h3>`;
        
        if (data.appearances.length === 0) {
            html += formatInfo('No appearances found');
        } else {
            html += '<table class="data-table"><thead><tr><th>Camera</th><th>Start Frame</th><th>End Frame</th></tr></thead><tbody>';
            data.appearances.forEach(app => {
                html += `<tr>
                    <td>Camera ${app.camera_id}</td>
                    <td>${app.start_frame}</td>
                    <td>${app.end_frame}</td>
                </tr>`;
            });
            html += '</tbody></table>';
        }
        
        showResult('objectResult', html);
    } catch (error) {
        showResult('objectResult', formatError(error.message));
    }
});

document.getElementById('btnFrames')?.addEventListener('click', async () => {
    const objectId = document.getElementById('objectId').value.trim();
    
    if (!objectId) {
        showResult('objectResult', formatError('Please enter an Object ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/frames?object_id=${objectId}`);
        
        let html = `<h3>Object ${objectId} Frame Segments</h3>`;
        
        if (data.segments.length === 0) {
            html += formatInfo('No segments found');
        } else {
            html += '<table class="data-table"><thead><tr><th>Camera</th><th>Start Frame</th><th>End Frame</th><th>Bboxes Count</th></tr></thead><tbody>';
            data.segments.forEach(seg => {
                html += `<tr>
                    <td>Camera ${seg.camera_id}</td>
                    <td>${seg.start_frame}</td>
                    <td>${seg.end_frame}</td>
                    <td>${seg.bboxes?.length || 0}</td>
                </tr>`;
            });
            html += '</tbody></table>';
        }
        
        showResult('objectResult', html);
    } catch (error) {
        showResult('objectResult', formatError(error.message));
    }
});

document.getElementById('btnDetails')?.addEventListener('click', async () => {
    const objectId = document.getElementById('objectId').value.trim();
    
    if (!objectId) {
        showResult('objectResult', formatError('Please enter an Object ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/details?object_id=${objectId}`);
        
        let html = `<h3>Object ${objectId} Details</h3>`;
        html += `<div class="result-item">
            <p><strong>Cameras Seen:</strong> ${data.cameras_seen.join(', ')}</p>
            <p><strong>Total Segments:</strong> ${data.total_segments}</p>
            <p><strong>Total Frames Visible:</strong> ${data.total_frames_visible}</p>
            <p><strong>Duration:</strong> ${data.duration_seconds} seconds</p>
        </div>`;
        
        showResult('objectResult', html);
    } catch (error) {
        showResult('objectResult', formatError(error.message));
    }
});

document.getElementById('btnClip')?.addEventListener('click', async () => {
    const objectId = document.getElementById('objectId').value.trim();
    
    if (!objectId) {
        showResult('objectResult', formatError('Please enter an Object ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/clip?object_id=${objectId}`);
        
        let html = `<h3>Object ${objectId} Clip</h3>`;
        html += formatSuccess('Clip generated successfully');
        html += `<div class="result-item">
            <p><strong>Clip URL:</strong> <a href="${data.clip_url}" target="_blank">${data.clip_url}</a></p>
            <button class="button button-primary" onclick="playVideo('${data.clip_url}')">Play Video</button>
        </div>`;
        
        showResult('objectResult', html);
    } catch (error) {
        showResult('objectResult', formatError(error.message));
    }
});

document.getElementById('btnLookup')?.addEventListener('click', async () => {
    const objectId = document.getElementById('lookupObjectId').value.trim();
    const frame = document.getElementById('lookupFrame').value.trim();
    
    if (!objectId || !frame) {
        showResult('lookupResult', formatError('Please enter both Object ID and Frame number'));
        return;
    }
    
    try {
        const data = await apiCall(`/frame_lookup?object_id=${objectId}&frame=${frame}`);
        
        let html = `<h3>Object ${objectId} at Frame ${frame}</h3>`;
        html += `<div class="result-item">
            <p><strong>Camera ID:</strong> ${data.camera_id}</p>
            <p><strong>Bounding Box (x, y, w, h):</strong> ${data.bbox.join(', ')}</p>
        </div>`;
        
        showResult('lookupResult', html);
    } catch (error) {
        showResult('lookupResult', formatError(error.message));
    }
});

/* ====================================
   Fences Tab - API Handlers
   ==================================== */

document.getElementById('btnListFences')?.addEventListener('click', async () => {
    try {
        const data = await apiCall('/fences');
        
        let html = '<h3>Available Fences</h3>';
        
        if (data.fences.length === 0) {
            html += formatInfo('No fences found');
        } else {
            html += '<div class="result-item">';
            data.fences.forEach(fence => {
                html += `<p>🚧 Fence: <strong>${fence}</strong></p>`;
            });
            html += '</div>';
        }
        
        showResult('fencesList', html);
    } catch (error) {
        showResult('fencesList', formatError(error.message));
    }
});

document.getElementById('btnFenceUsage')?.addEventListener('click', async () => {
    const fenceId = document.getElementById('fenceId').value.trim();
    if (!fenceId) {
        showResult('fenceResult', formatError('Please enter a Fence ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/fence_usage?fence_id=${fenceId}`);
        
        let html = `<h3>Fence ${fenceId} Usage</h3>`;
        
        if (Array.isArray(data.usage) && data.usage.length === 0) {
            html += formatInfo('No usage data available');
        } else if (Array.isArray(data.usage)) {
            html += '<table class="data-table"><thead><tr><th>Object ID</th><th>Timestamp</th><th>Event Type</th></tr></thead><tbody>';
            data.usage.forEach(event => {
                html += `<tr>
                    <td>${event.object_id ?? 'N/A'}</td>
                    <td>${event.frame ?? 'N/A'}</td>
                    <td>${event.event ?? 'N/A'}</td>
                </tr>`;
            });
            html += '</tbody></table>';
        } else {
            html += `<div class="result-item"><pre>${JSON.stringify(data.usage, null, 2)}</pre></div>`;
        }
        
        showResult('fenceResult', html);
    } catch (error) {
        showResult('fenceResult', formatError(error.message));
    }
});

/* ====================================
   Gates Tab - API Handlers
   ==================================== */

document.getElementById('btnGateSequence')?.addEventListener('click', async () => {
    const objectId = document.getElementById('gateObjectId').value.trim();
    
    if (!objectId) {
        showResult('gateSequenceResult', formatError('Please enter an Object ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/gate_sequence?object_id=${objectId}`);
        
        let html = `<h3>Gate Entry/Exit Sequence - Object ${objectId}</h3>`;
        
        if (data.gate_sequence.length === 0) {
            html += formatInfo('No gate activity found');
        } else {
            html += '<table class="data-table"><thead><tr><th>Gate</th><th>Frame</th><th>Event Type</th><th>Timestamp</th></tr></thead><tbody>';
            data.gate_sequence.forEach(events => {
                html += `<tr>
                    <td>${events.fence ?? 'N/A'}</td>
                    <td>${events.frame ?? 'N/A'}</td>
                    <td>${events.event ?? 'N/A'}</td>
                    <td>${events.frame ?? 'N/A'}</td>
                </tr>`;
            });
            html += '</tbody></table>';
        }
        
        showResult('gateSequenceResult', html);
    } catch (error) {
        showResult('gateSequenceResult', formatError(error.message));
    }
});

document.getElementById('btnGateClip')?.addEventListener('click', async () => {
    const objectId = document.getElementById('gateClipObjectId').value.trim();
    const frame = document.getElementById('gateClipFrame').value.trim();
    const camera = document.getElementById('gateClipCamera').value.trim();
    
    if (!objectId || !frame || !camera) {
        showResult('gateClipResult', formatError('Please enter Object ID, Frame number, and Camera ID'));
        return;
    }
    
    try {
        const data = await apiCall(`/gate_clip?object_id=${objectId}&frame=${frame}&camera=${camera}`);
        
        let html = `<h3>Gate Clip - Object ${objectId}</h3>`;
        html += formatSuccess('Gate clip generated successfully');
        html += `<div class="result-item">
            <p><strong>Clip URL:</strong> <a href="${data.clip_url}" target="_blank">${data.clip_url}</a></p>
            <button class="button button-primary" onclick="playVideo('${data.clip_url}')">Play Video</button>
        </div>`;
        
        showResult('gateClipResult', html);
    } catch (error) {
        showResult('gateClipResult', formatError(error.message));
    }
});

/* ====================================
   Chat Interface
   ==================================== */

const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

function addChatMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    if (!isUser) {
        messageDiv.innerHTML = `<strong>${isUser ? 'You' : 'Assistant'}:</strong> ${text}`;
    } else {
        messageDiv.textContent = text;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatSendBtn?.addEventListener('click', sendChatMessage);
chatInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

async function sendChatMessage() {
    const query = chatInput.value.trim();
    
    if (!query) return;
    
    // Add user message to chat
    addChatMessage(query, true);
    chatInput.value = '';
    
    try {
        const response = await apiCall('/chat', 'POST', { query });
        
        let botResponse = '';
        
        if (response.tool_used) {
            botResponse = `Used tool: <strong>${response.tool_used}</strong>\n\n`;
            botResponse += `Result: ${JSON.stringify(response.result, null, 2)}`;
        } else if (response.llm_response) {
            botResponse = response.llm_response;
        }
        
        addChatMessage(botResponse, false);
    } catch (error) {
        addChatMessage(`Error: ${error.message}`, false);
    }
}

/* ====================================
   Video Player Modal
   ==================================== */

function playVideo(videoUrl) {
    modal.classList.add('show');
    videoPlayer.src = videoUrl;
    videoPlayer.play();
}

closeBtn?.addEventListener('click', () => {
    modal.classList.remove('show');
    videoPlayer.pause();
    videoPlayer.src = '';
});

modal?.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('show');
        videoPlayer.pause();
        videoPlayer.src = '';
    }
});

/* ====================================
   Document Ready
   ==================================== */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Video Analytics Dashboard loaded');
});
