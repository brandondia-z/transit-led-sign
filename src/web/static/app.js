document.addEventListener('DOMContentLoaded', async () => {
    let allStations = [];
    let allLines = [];
    let currentConfig = {};
    let selectedLine = null;
    let selectedStationCode = null;
    let selectedDirection = 'all';

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

        // Try to deduce selected line from station code
        const currentStation = allStations.find(s => s.Code === selectedStationCode);
        if (currentStation) {
            selectLine(currentStation.LineCode1); // Default to the first line of the station
        } else {
            selectLine('SV'); // Default fallback
        }
        
        updateDirectionUI(selectedDirection);

    } catch (e) {
        console.error("Failed to initialize app:", e);
    }

    // 2. Setup Event Listeners
    brightnessSlider.addEventListener('input', (e) => {
        brightnessVal.textContent = `${e.target.value}%`;
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
});
