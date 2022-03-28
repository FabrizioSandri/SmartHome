function generateCameraSelector(id, camerasJson) {

    selectCamera = document.getElementById(`cameras${id}`);

    camerasJson.forEach((camera) => {
        let optionCamera = document.createElement("option");
        optionCamera.setAttribute("value", "" + camera);
        optionCamera.innerText = camera;
        
        selectCamera.appendChild(optionCamera);
    });
    
}

function switchCamera(id) {
    console.log(`camera${id}`)
    cameraView = document.getElementById(`camera${id}`);
    newCameraid = document.getElementById(`cameras${id}`).value;
    
    console.log(`/surveillance/video_feed?cameraid=${newCameraid}`)
    cameraView.setAttribute("src", `/surveillance/video_feed?cameraid=${newCameraid}`)
}

/**
 * Dynamically generate the camera layout with a total of "numCameras" cameras
 */
function generateCameraLayout(rows, cols, camerasJson){
    let containerDiv = document.getElementById("mainContainer");
    containerDiv.innerHTML = '';

    for (let row = 0; row < rows; row++) {
        let rowDiv = document.createElement("div");
        rowDiv.classList.add("row", "justify-content-center");

        containerDiv.appendChild(rowDiv);

        for (let col = 0; col < cols; col++) {
            let colDiv = document.createElement("div");
            colDiv.classList.add("col");

            let id = row*cols + col; // the id is given by the number of cells already added

            let row1Div = document.createElement("div");
            let row2Div = document.createElement("div");

            row1Div.classList.add("row", "justify-content-center");
            row2Div.classList.add("row", "justify-content-center");

            let selectCamera = document.createElement("select");
            selectCamera.id = `cameras${id}`;

            let btnView = document.createElement("button");
            btnView.innerText = "Seleziona";
            btnView.onclick = () => switchCamera(id);
            btnView.classList.add("btn", "btn-secondary");

            var cameraView = document.createElement("img");
            cameraView.id = `camera${id}`;
            cameraView.src = "static/empty.png";
            cameraView.alt = "";
            cameraView.style.width = "100%";
            cameraView.classList.add("cameraview");
            cameraView.onerror = () => cameraView.src='static/empty.png';
            
            rowDiv.appendChild(colDiv);

            // the select button on the second line will be at the bottom
            if (row == 1){
                colDiv.appendChild(row2Div);
                colDiv.appendChild(row1Div);
            }else{
                colDiv.appendChild(row1Div);
                colDiv.appendChild(row2Div);
            }
            
            row1Div.appendChild(selectCamera);
            row1Div.appendChild(btnView);
            row2Div.appendChild(cameraView);

            generateCameraSelector(id, camerasJson);
        }
    }

    // if a single camera reduce the size of the box
    if (rows==1 && cols==1 && window.matchMedia("(min-width: 43em)").matches){
        cameraView.style.width = "80%";
    }
    
}