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