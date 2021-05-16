const socket = io();
let config = {};  // Holds the latest config from the server

socket.on("message", function (data) {
    console.log(data);
    recievedFromSocket(data);
});

socket.on("connect", function (data) {
    console.log("Connected to socket");
});

socket.on("disconnect", function (data) {
    console.log("Disconneted from socket");
});

function sendToSocket(json) {
    socket.send(json);
    console.log("sent " + json);
}

function recievedFromSocket(json) {
    console.log("received " + json);
    config = json;
    updatePageFromConfig();
}

// Read from `config` and update any necessary elements
function updatePageFromConfig() {
    console.log(config.selectables);
    for (let [selectableName, selectableProperies] of Object.entries(config.selectables)) {
        let className = "selectable_" + selectableName;
        let selectableBoxes = document.getElementsByClassName(className);
        console.log(selectableProperies);
        console.log(selectableBoxes);
        let text;
        let enabled = true;
        if (selectableProperies.value === "") {
            // This selectable isn't selected
            text = selectableProperies.empty_text;
            enabled = false;
        } else {
            text = `${selectableProperies.prefix}${selectableProperies.value}${selectableProperies.suffix}`;
        }

        for (let div of selectableBoxes) {
            console.log(div);
            div.innerHTML = text;
            if (enabled) {
                div.classList.remove("selectable_disabled");
            } else {
                div.classList.add("selectable_disabled");
            }
        }
    }
}

// Show the selection box under parentElement with results from selectableName
function showSelectionBox(parentElement, selectableName) {
    // Show the invisible div so that when you click off the selection box, it closes
    let invisibleDiv = document.getElementById("invisibleDiv");
    invisibleDiv.style.display = "inline-block";
    console.log(parentElement, selectableName);

    let header = document.getElementById("selectionBoxHeader");
    header.innerHTML = config.selectables[selectableName].friendly_name;

    let body = document.getElementById("selectionBoxBody");
    let newBodyHtml = '<p class="control has-icons-left">' +
        `<input id="searchField" class="input" type="text" placeholder="Search" oninput="updateSearchFilter(this.value, '${selectableName}');">` +
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
        newBodyHtml += `<div class="selectableListElement searchResult" onclick="setSelectable('${selectableName}', '${selectable}');">${selectable}</div>`;
    }

    newBodyHtml += `<div id="addSelectableDiv" class="selectableListElement"><i class="fa fa-plus"></i> ${selectableProperties.add_text}<span id="addSelectableText"></span></div>`;
    newBodyHtml += '</div>';

    body.innerHTML = newBodyHtml;
    updateSearchFilter("", selectableName);
}

function updateSearchFilter(text, selectableName) {
    let textLower = text.toLowerCase();
    // Filter search results
    let searchDivs = document.getElementsByClassName("searchResult");
    for (let result of searchDivs) {
        if (result.innerHTML.toLowerCase().includes(textLower)) {
            result.style.display = "";
        } else {
            result.style.display = "none";
        }
    }

    let addSelectableDiv = document.getElementById("addSelectableDiv");
    // Updaate the "add" text and click action
    let selectableText = document.getElementById("addSelectableText");
    if (text === "") {
        selectableText.innerHTML = " (Use Search)";
        addSelectableDiv.onclick = function () {
            let searchField = document.getElementById("searchField");
            searchField.focus();
        };
    } else {
        selectableText.innerHTML = `: "${text}"`;
        addSelectableDiv.setAttribute("oncLick",  `addSelectable('${selectableName}', '${text}');`);
    }




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
    invisibleDiv.style.display = "none";
}

function addSelectable(selectableType, value) {
    console.log("Adding selectable ", selectableType, value);
}

function deleteSelectable(selectableType, value) {
    console.log("Deleting selectable ", selectableType, value);
}

function setSelectable(selectableType, value) {
    console.log("Setting selectable ", selectableType, value);
}