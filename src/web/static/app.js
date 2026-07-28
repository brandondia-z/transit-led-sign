document.addEventListener('DOMContentLoaded', async () => {
    let allStations = [];
    let allLines = [];
    let currentConfig = {};
    let selectedLine = null;
    let selectedStationCode = null;
    let selectedDirection = 'all';
    let selectedMode = 'transit';

    const stationSelect = document.getElementById('stationSelect');
    const lineBtns = document.querySelectorAll('.line-btn');
    const directionBtns = document.querySelectorAll('.segment');
    const saveBtn = document.getElementById('saveBtn');
    const toast = document.getElementById('toast');
    const dir1Btn = document.getElementById('dir1Btn');
    const dir2Btn = document.getElementById('dir2Btn');
    const brightnessSlider = document.getElementById('brightnessSlider');
    const brightnessVal = document.getElementById('brightnessVal');

    // 1. Fetch initial data
    try {
        const [configRes, stationsRes, linesRes] = await Promise.all([
            fetch('/api/config'),
            fetch('/api/stations'),
            fetch('/api/lines')
        ]);
        
        currentConfig = await configRes.json();
        allStations = await stationsRes.json();
        allLines = await linesRes.json();

        // Initial UI State setup based on config
        selectedStationCode = currentConfig.station_codes;
        selectedDirection = currentConfig.direction_group;
        brightnessSlider.value = currentConfig.brightness || 60;
        brightnessVal.textContent = `${brightnessSlider.value}%`;
        selectedMode = currentConfig.display_mode || 'transit';
        
        // Setup Canvas Data if available
        if (currentConfig.canvas_data && currentConfig.canvas_data.length === 2048) {
            canvasData = currentConfig.canvas_data;
            renderCanvasFromData();
        }

        // Try to deduce selected line from station code
        const currentStation = allStations.find(s => s.Code === selectedStationCode);
        if (currentStation) {
            selectLine(currentStation.LineCode1); // Default to the first line of the station
        } else {
            selectLine('SV'); // Default fallback
        }
        
        updateDirectionUI(selectedDirection);
        updateModeUI(selectedMode);

    } catch (e) {
        console.error("Failed to initialize app:", e);
    }

    // 2. Setup Event Listeners
    const brightDownBtn = document.getElementById('brightDownBtn');
    const brightUpBtn = document.getElementById('brightUpBtn');

    function updateBrightness(val) {
        let newVal = Math.max(1, Math.min(100, val));
        brightnessSlider.value = newVal;
        brightnessVal.textContent = `${newVal}%`;
    }

    brightnessSlider.addEventListener('input', (e) => {
        updateBrightness(parseInt(e.target.value, 10));
    });

    brightDownBtn.addEventListener('click', () => {
        updateBrightness(parseInt(brightnessSlider.value, 10) - 5);
    });

    brightUpBtn.addEventListener('click', () => {
        updateBrightness(parseInt(brightnessSlider.value, 10) + 5);
    });

    lineBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            selectLine(btn.dataset.line);
        });
    });

    stationSelect.addEventListener('change', (e) => {
        selectedStationCode = e.target.value;
    });

    directionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            selectedDirection = btn.dataset.direction;
            updateDirectionUI(selectedDirection);
        });
    });

    saveBtn.addEventListener('click', async () => {
        const payload = {
            station_codes: selectedStationCode,
            direction_group: selectedDirection,
            station_name: stationSelect.options[stationSelect.selectedIndex]?.text || "Station",
            direction_name: selectedDirection === '1' ? dir1Btn.textContent : (selectedDirection === '2' ? dir2Btn.textContent : 'Both Directions'),
            brightness: parseInt(brightnessSlider.value, 10)
        };
        
        saveBtn.innerText = "Saving...";
        
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            showToast();
        } catch (e) {
            console.error(e);
            alert("Failed to save settings");
        } finally {
            saveBtn.innerText = "Save Settings";
        }
    });

    // 3. Helper Functions
    function selectLine(lineCode) {
        selectedLine = lineCode;
        
        // Update Buttons
        lineBtns.forEach(btn => {
            if (btn.dataset.line === lineCode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Filter Stations for this line
        const lineStations = allStations.filter(s => 
            s.LineCode1 === lineCode || 
            s.LineCode2 === lineCode || 
            s.LineCode3 === lineCode || 
            s.LineCode4 === lineCode
        ).sort((a, b) => a.Name.localeCompare(b.Name));

        // Populate Dropdown
        stationSelect.innerHTML = '';
        stationSelect.disabled = false;
        
        let foundCurrent = false;
        lineStations.forEach(s => {
            const option = document.createElement('option');
            option.value = s.Code;
            option.textContent = s.Name;
            stationSelect.appendChild(option);
            
            if (s.Code === selectedStationCode) foundCurrent = true;
        });

        // If the previously selected station isn't on this line, select the first one
        if (foundCurrent) {
            stationSelect.value = selectedStationCode;
        } else if (lineStations.length > 0) {
            stationSelect.value = lineStations[0].Code;
            selectedStationCode = lineStations[0].Code;
        }

        // Update Direction Terminals
        const lineData = allLines.find(l => l.LineCode === lineCode);
        if (lineData) {
            const startStation = allStations.find(s => s.Code === lineData.StartStationCode);
            const endStation = allStations.find(s => s.Code === lineData.EndStationCode);
            
            dir1Btn.textContent = endStation ? endStation.Name : "Direction 1";
            dir2Btn.textContent = startStation ? startStation.Name : "Direction 2";
        }
    }

    function updateDirectionUI(dir) {
        directionBtns.forEach(btn => {
            if (btn.dataset.direction === dir) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    function showToast() {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
    }

    // --- Mode Selector Logic ---
    const modeBtns = document.querySelectorAll('#modeSelector .segment');
    const transitSection = document.getElementById('transitSection');
    const canvasSection = document.getElementById('canvasSection');
    const saveBtnContainer = document.getElementById('saveBtn');

    function updateModeUI(mode) {
        modeBtns.forEach(btn => {
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        if (mode === 'transit') {
            transitSection.style.display = 'block';
            canvasSection.style.display = 'none';
            saveBtnContainer.style.display = 'block';
        } else {
            transitSection.style.display = 'none';
            canvasSection.style.display = 'block';
            saveBtnContainer.style.display = 'none';
        }
    }

    modeBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            selectedMode = btn.dataset.mode;
            updateModeUI(selectedMode);
            // Instantly save mode change
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ display_mode: selectedMode })
            });
        });
    });

    // --- Canvas Drawing Logic ---
    const ledCanvas = document.getElementById('ledCanvas');
    const ctx = ledCanvas.getContext('2d');
    let isDrawing = false;
    let currentColor = '#E51636';
    let canvasData = new Array(64 * 32).fill('#000000');

    // Initialize canvas to black visually
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 64, 32);

    function renderCanvasFromData() {
        for (let y = 0; y < 32; y++) {
            for (let x = 0; x < 64; x++) {
                ctx.fillStyle = canvasData[y * 64 + x] || '#000000';
                ctx.fillRect(x, y, 1, 1);
            }
        }
    }

    function getMousePos(e) {
        const rect = ledCanvas.getBoundingClientRect();
        // Calculate scale since CSS scales the canvas up
        const scaleX = ledCanvas.width / rect.width;
        const scaleY = ledCanvas.height / rect.height;
        
        let clientX = e.clientX;
        let clientY = e.clientY;
        
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        }

        const x = Math.floor((clientX - rect.left) * scaleX);
        const y = Math.floor((clientY - rect.top) * scaleY);
        return { x, y };
    }

    function drawPixel(e) {
        const { x, y } = getMousePos(e);
        if (x >= 0 && x < 64 && y >= 0 && y < 32) {
            // Update visual canvas
            ctx.fillStyle = currentColor;
            ctx.fillRect(x, y, 1, 1);
            // Update data model
            canvasData[y * 64 + x] = currentColor;
        }
    }

    // Mouse Events
    ledCanvas.addEventListener('mousedown', (e) => { isDrawing = true; drawPixel(e); });
    ledCanvas.addEventListener('mousemove', (e) => { if (isDrawing) drawPixel(e); });
    ledCanvas.addEventListener('mouseup', () => { isDrawing = false; });
    ledCanvas.addEventListener('mouseleave', () => { isDrawing = false; });

    // Touch Events (prevent scrolling while drawing)
    ledCanvas.addEventListener('touchstart', (e) => { e.preventDefault(); isDrawing = true; drawPixel(e); }, {passive: false});
    ledCanvas.addEventListener('touchmove', (e) => { e.preventDefault(); if (isDrawing) drawPixel(e); }, {passive: false});
    ledCanvas.addEventListener('touchend', (e) => { e.preventDefault(); isDrawing = false; });

    // Color Palette
    const colorBtns = document.querySelectorAll('.color-btn');
    const customColorPicker = document.getElementById('customColorPicker');
    
    colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentColor = btn.dataset.color;
        });
    });

    customColorPicker.addEventListener('input', (e) => {
        currentColor = e.target.value;
    });

    // Send and Clear Buttons
    const sendCanvasBtn = document.getElementById('sendCanvasBtn');
    const clearCanvasBtn = document.getElementById('clearCanvasBtn');

    clearCanvasBtn.addEventListener('click', () => {
        canvasData.fill('#000000');
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, 64, 32);
    });

    sendCanvasBtn.addEventListener('click', async () => {
        sendCanvasBtn.innerText = "Sending...";
        try {
            await fetch('/api/canvas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ canvas_data: canvasData })
            });
            showToast();
        } catch (e) {
            console.error(e);
            alert("Failed to send drawing");
        } finally {
            sendCanvasBtn.innerText = "Send to Sign";
        }
    });

});
