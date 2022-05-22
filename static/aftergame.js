const socket = io();
let config = {};  // Holds the latest config from the server

socket.on("message", function (data) {
    receivedFromSocket(data);
});

socket.on("toast", function (data) {
    handleToast(data);
});

socket.on("connect", function (data) {
    showTab("mainTab");
    let footer = document.getElementById("footer");
    footer.style.display = "inline-block";
});

socket.on("disconnect", function (data) {
    showTab("loadingTab");
    hideSelectionBox();
    let footer = document.getElementById("footer");
    footer.style.display = "none";
});

function sendToSocket(json) {
    socket.send(json);
}

function receivedFromSocket(json) {
    config = json;
    updatePageFromConfig();
}

document.addEventListener("keypress", keyPressed);

function handleToast(data) {
    let toastBox = document.getElementById("toastBox");
    let toast = document.createElement("div");
    toast.innerHTML = data.message;
    toast.classList = `toast ${data.style}`;
    toastBox.appendChild(toast);

    // Hide the toast message after 5 seconds
    setTimeout(function () {
        toast.remove();
    }, 5000);
}

function positionSelectionBox(parent) {
    // parent is the element that the user clicked to show this
    let selectionBox = document.getElementById("selectionBox");
    // Horizontal position
    // Get the centerX of the clicked element
    let centerX = parent.offsetLeft + parent.offsetWidth / 2;
    // Calculate the ideal X for the selection box
    let selectionBoxX = centerX - selectionBox.offsetWidth / 2;
    // Make sure that it doesn't leave the viewport
    // The order is important to default to being cut off to the right if the viewport is too small
    selectionBoxX = Math.min(selectionBoxX, window.innerWidth - selectionBox.offsetWidth); // Prevent going further right than the window width
    selectionBoxX = Math.max(selectionBoxX, 0); // Prevent going further left than 0
    selectionBox.style.left = `${selectionBoxX}px`;

    // Vertical position
    let downwardShift = 5;
    let selectionBoxY = parent.offsetTop + parent.offsetHeight + downwardShift;
    selectionBox.style.top = `${selectionBoxY}px`;

    // Resize the page to accommodate the selection box if necessary
    let invisibleDiv = document.getElementById("invisibleDiv");
    invisibleDiv.style.height = `${document.documentElement.scrollHeight}px`;
}

// Read from `config` and update any necessary elements
function updatePageFromConfig() {
    // Build the selectables area
    for (let [selectableName, selectableProperties] of Object.entries(config.selectables)) {
        let className = "selectable_" + selectableName;
        let selectableBoxes = document.getElementsByClassName(className);
        let text;
        let enabled = true;
        if (selectableProperties.value === "") {
            // This selectable isn't selected
            text = selectableProperties.empty_text;
            enabled = false;
        } else {
            text = `${selectableProperties.prefix}${selectableProperties.value}${selectableProperties.suffix}`;
        }

        for (let div of selectableBoxes) {
            div.innerHTML = text;
            if (enabled) {
                div.classList.remove("selectable_disabled");
            } else {
                div.classList.add("selectable_disabled");
            }
        }
    }

    // Build the recent recordings area
    let recordingsContainer = document.getElementById("recent-recordings-box");
    recordingsContainer.innerHTML = ""; // Empty the div
    let recordings = config.recent_recordings;
    for (let recording of recordings) {
        let row = document.createElement("div");

        // Create the left column for the time
        let left = document.createElement("div");
        left.classList.add("recent-recordings-left");
        let timestampElement = document.createElement("p");
        timestampElement.classList.add("recent-recordings-row-hover-element");
        let recordingDate = new Date(recording.timestamp * 1000); // Convert the UNIX timestamp to be human-readable
        timestampElement.innerHTML = recordingDate.toLocaleString();
        left.appendChild(timestampElement);

        // Create the middle column for the file location
        let middle = document.createElement("div");
        middle.classList.add("recent-recordings-middle");
        let filePathTextElement = document.createElement("p");
        filePathTextElement.innerText = recording.current_path;
        middle.appendChild(filePathTextElement);

        // Create the right column for the update button
        let right = document.createElement("div");
        right.classList.add("recent-recordings-right");
        let updateRecordingElement = document.createElement("button");
        updateRecordingElement.classList.add("normal-button", "recent-recordings-row-hover-element");
        updateRecordingElement.innerText = "Update";
        updateRecordingElement.onclick = function () {
            updateOldRecording(recording.current_path);
        };
        right.appendChild(updateRecordingElement);

        row.append(left, middle, right);
        row.classList.add("recent-recordings-row");
        recordingsContainer.appendChild(row);
    }
}

// Show the selection box under parentElement with results from selectableName
function showSelectionBox(parentElement, selectableName) {
    // Show the invisible div so that when you click off the selection box, it closes
    let invisibleDiv = document.getElementById("invisibleDiv");
    invisibleDiv.style.display = "inline-block";

    let header = document.getElementById("selectionBoxHeader");
    header.innerHTML = config.selectables[selectableName].friendly_name;

    let body = document.getElementById("selectionBoxBody");
    let newBodyHtml = '<p class="control has-icons-left">' +
        `<input id="searchField" class="input" type="text" placeholder="Search" autocomplete="off" oninput="updateSearchFilter(this.value, '${selectableName}');"/>` +
        '<span class="icon is-small is-left">' +
        '<i class="fas fa-search"></i>' +
        '</span>' +
        '</p>';
    newBodyHtml += '<div class="selectableListRegion">';

    let selectableProperties = config.selectables[selectableName];
    let selectableOptionsName = selectableProperties.options;
    let options = config.selectable_options[selectableOptionsName];
    newBodyHtml += `<div class="selectableListElement" onclick="setSelectable('${selectableName}', '');"><i class="fa fa-times"></i> ${selectableProperties.empty_text}</div>`;
    for (let selectable of options) {
        newBodyHtml += `<div class="selectableListElement searchResult" onclick="setSelectable('${selectableName}', '${selectable}');">
            ${selectable}
            <div class="delete-selectable" onclick="deleteSelectable('${selectableName}', '${selectable}'); hideSelectionBox(); event.stopPropagation();"><i class="fa fa-backspace"></i></div>
        </div>`;
    }

    newBodyHtml += `<div id="addSelectableDiv" class="selectableListElement"><i class="fa fa-plus"></i> ${selectableProperties.add_text}<span id="addSelectableText"></span></div>`;
    newBodyHtml += '</div>';

    body.innerHTML = newBodyHtml;
    body.scrollTop = 0; // Always scroll to the top when opening the box
    positionSelectionBox(parentElement);
    updateSearchFilter("", selectableName);
}

function updateSearchFilter(text, selectableName) {
    let textLower = text.toLowerCase();
    // Filter search results
    let searchDivs = document.getElementsByClassName("searchResult");
    for (let result of searchDivs) {
        if (result.innerText.toLowerCase().includes(textLower)) {
            result.style.display = "";
        } else {
            result.style.display = "none";
        }
    }

    let addSelectableDiv = document.getElementById("addSelectableDiv");
    // Update the "add" text and click action
    let selectableText = document.getElementById("addSelectableText");
    if (text === "") {
        selectableText.innerHTML = " (Use Search)";
        addSelectableDiv.onclick = function () {
            let searchField = document.getElementById("searchField");
            searchField.focus();
        };
    } else {
        selectableText.innerHTML = `: "${text}"`;
        addSelectableDiv.setAttribute("oncLick", `addSelectable('${selectableName}', '${text}');`);
    }
}

function showNewPrestBox(parent) {
    let invisibleDiv = document.getElementById("invisibleDiv");
    invisibleDiv.style.display = "inline-block";

    let header = document.getElementById("selectionBoxHeader");
    header.innerHTML = "New Preset";

    let body = document.getElementById("selectionBoxBody");
    let newBodyHtml = '<p>Scan a barcode to add the following configuration as a preset.</p>';
    newBodyHtml += '<p class="control has-icons-left">' +
        `<input id="newPresetBarcodeField" class="input" type="text" placeholder="Barcode" autocomplete="off" onkeyup="inputEnterAction(this.value, addPreset);"/>` +
        '<span class="icon is-small is-left">' +
        '<i class="fas fa-barcode"></i>' +
        '</span>' +
        '</p>';

    for (let [selectableName, value] of Object.entries(getCurrentSettingsAsPreset())) {
        newBodyHtml += `<div class="medium-text">${config.selectables[selectableName].friendly_name}: <span class="primary-text">${value}</span></div>`;
    }

    body.innerHTML = newBodyHtml;
    body.scrollTop = 0; // Always scroll to the top when opening the box
    positionSelectionBox(parent); // Put the box in the right place
    let barcodeInput = document.getElementById("newPresetBarcodeField");
    barcodeInput.focus(); // Bring focus to this input so a barcode scanner is ready to go
}

// Gets called any time the invisible div is clicked
function hideSelectionBoxListener(e) {
    let invisibleDiv = document.getElementById("invisibleDiv");
    if (e.target === invisibleDiv) {
        hideSelectionBox();
    }
}

function hideSelectionBox() {
    let invisibleDiv = document.getElementById("invisibleDiv");
    invisibleDiv.style.height = ""; // Reset the div's height
    invisibleDiv.style.display = "none";
}

// Call func with text if event == enter key pressed
function inputEnterAction(text, func) {
    if (event.key === "Enter") {
        func(text);
    }
}

function getCurrentSettingsAsPreset() {
    let preset = {};
    for (let [selectableName, selectableProperties] of Object.entries(config.selectables)) {
        let value = selectableProperties.value;
        if (value !== "") {
            preset[selectableName] = value;
        }
    }
    return preset;
}

function addSelectable(selectableType, value) {
    hideSelectionBox();
    let response = {
        "action": "add_selectable",
        "selectable_type": selectableType,
        "value": value
    };
    sendToSocket(response);
}

function deleteSelectable(selectableType, value) {
    let response = {
        "action": "delete_selectable",
        "selectable_type": selectableType,
        "value": value
    };
    sendToSocket(response);
}

function setSelectable(selectableType, value) {
    hideSelectionBox();
    let response = {
        "action": "set_selectable",
        "selectable_type": selectableType,
        "value": value
    };
    sendToSocket(response);
}

function addPreset(barcode) {
    hideSelectionBox();
    let response = {
        "action": "add_preset",
        "barcode": barcode,
        "preset": JSON.stringify(getCurrentSettingsAsPreset())
    };
    sendToSocket(response);
}

function loadPreset(barcode) {
    let presetField = document.getElementById("loadPresetField");
    presetField.value = "";
    let response = {
        "action": "load_preset",
        "barcode": barcode,
    };
    sendToSocket(response);
}

function addBulkGame() {
    let titleField = document.getElementById("bulkGameTitle");
    let platformField = document.getElementById("bulkGamePlatform");
    let barcodesField = document.getElementById("bulkGameBarcodes");
    let title = titleField.value;
    let platform = platformField.value;
    let barcodes = new Set(barcodesField.value.split("\n"));
    // Clear the typing fields
    titleField.value = "";
    barcodesField.value = "";
    updateBulkPreview();
    let response = {
        "action": "add_bulk_game",
        "title": title,
        "platform": platform,
        "barcodes": Array.from(barcodes),
    };
    sendToSocket(response);
}

function updateOldRecording(path) {
    let response = {
        "action": "update_old_recording",
        "path": path,
    };
    sendToSocket(response);
}

function updateBulkPreview() {
    let titleField = document.getElementById("bulkGameTitle");
    let platformField = document.getElementById("bulkGamePlatform");
    let barcodesField = document.getElementById("bulkGameBarcodes");
    let gamePreview = document.getElementById("bulkGameAdderGamePreview");
    let platformPreview = document.getElementById("bulkGameAdderPlatformPreview");
    let barcodesPreview = document.getElementById("bulkGameAdderBarcodes");

    let barcodes = new Set(barcodesField.value.split("\n"));
    let barcodesPreviewText = "";
    for (let barcode of barcodes) {
        barcodesPreviewText += `<div class="medium-text primary-text">${barcode}</div>`
    }

    gamePreview.innerHTML = titleField.value;
    platformPreview.innerHTML = platformField.value;
    barcodesPreview.innerHTML = barcodesPreviewText;
}

function showTab(tabId) {
    let allTabs = document.getElementsByClassName("tab");
    for (let tab of allTabs) {
        if (tab.id !== tabId) {
            tab.style.display = "none";
        } else {
            tab.style.display = "inline-block"; // Default visibility
        }
    }
}

// Handle scanning barcodes without activating the text field
function keyPressed(event) {
    if (event.target.type !== "input") {
        let presetField = document.getElementById("loadPresetField");
        presetField.focus();
    }
}