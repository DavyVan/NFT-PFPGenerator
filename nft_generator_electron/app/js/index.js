'use strict';

const path = require("path");
const fs = require("fs");
const {ipcRenderer, dialog} = require("electron");
const remote = require("@electron/remote");
const axios = require("axios").default;

const baseURL = "http://localhost:23333/local_api/";

/* -------------------------------- Elements -------------------------------- */

let overlayDivEl = document.getElementById("overlay");
let inputFolderInputEl = document.getElementById("input-folder-input");
let inputFolderBtnEl = document.getElementById("input-folder-button");
let outputFolderInputEl = document.getElementById("output-folder-input");
let outputFolderBtnEl = document.getElementById("output-folder-button");
let resourceSizeInputEl = document.getElementById("resource-size-input");
let collectionNameInputEl = document.getElementById("collection-name-input");
let metadataSelectEl = document.getElementById("metadata-std-select");
let countInputEl = document.getElementById("count-input");
let progressBarEl = document.getElementById("progress-bar");
let startBtnEl = document.getElementById("start-button");
let serverStatusSpinnerEl = document.getElementById("server-status-spinner");
let serverStatusSpanEl = document.getElementById("server-status-span");
let alertMsgSpanEl = document.getElementById("alert-msg-span");
let excelCheckboxEl = document.getElementById("excel-checkbox");
let metadataCheckboxEl = document.getElementById("metadata-checkbox");
let startingIndexInputEl = document.getElementById("starting-index-input");

let inputFolderInputStep2El = document.getElementById("input-folder-input-step-2");
let inputFolderBtnStep2El = document.getElementById("input-folder-button-step-2");
let outputFolderInputStep2El = document.getElementById("output-folder-input-step-2");
let deleteCheckboxStep2El = document.getElementById("delete-checkbox-step-2");
let reorderCheckboxStep2El = document.getElementById("reorder-checkbox-step-2");
let metadataSelectStep2El = document.getElementById("metadata-std-select-step-2");
let alertMsgSpanStep2El = document.getElementById("alert-msg-span-step-2");
let startBtnStep2El = document.getElementById("start-button-step-2");
let collectionNameInputStep2El = document.getElementById("collection-name-input-step-2");

let step1BtnEl = document.getElementById("step-1-button");
let step2BtnEl = document.getElementById("step-2-button");
let step1ContainerEl = document.getElementById("step-1-container");
let step2ContainerEl = document.getElementById("step-2-container");


/* ------------------------------- NFGT Server ------------------------------ */

setInterval(() => {
    axios.get(baseURL + "ping").then((response) => {
        // console.log("index: NFGT Server is running. pid: %d", response.data.data.pid);
        ipcRenderer.invoke("pid", response.data.data.pid);
        overlayDivEl.hidden = true;
        serverStatusSpinnerEl.classList.remove("text-danger");
        serverStatusSpinnerEl.classList.add("text-success");
        serverStatusSpanEl.innerHTML = "图像处理服务运行中";
    }).catch(() => {
        serverStatusSpinnerEl.classList.remove("text-success");
        serverStatusSpinnerEl.classList.add("text-danger");
        serverStatusSpanEl.innerHTML = "图像处理服务状态未知";
    });
}, 5*1000);


/* -------------------------------- 第一步 ------------------------------- */

inputFolderBtnEl.addEventListener("click", () => {
    remote.dialog.showOpenDialog(remote.getCurrentWindow(), {
        title: "选择素材文件夹",
        buttonLabel: "选择",
        properties: ["openDirectory"]
    }).then((value) => {
        let folderNames = value.filePaths;
        if (value.canceled) {
            console.log("inputFolderBtnEl-click: no input folder selected.");
            return;     // do nothing
        }
    
        let folderName = folderNames[0];
    
        // update DOM
        inputFolderInputEl.value = folderName;
        let _v = outputFolderInputEl.value;
        if (_v == "" || _v == undefined || _v == null) {
            outputFolderInputEl.value = path.join(folderName, "output");      // only auto fill when empty
        }
    });
});

outputFolderBtnEl.addEventListener("click", () => {
    remote.dialog.showOpenDialog(remote.getCurrentWindow(), {
        title: "选择输出文件夹",
        buttonLabel: "选择",
        properties: ["openDirectory", "createDirectory", "promptToCreate", "dontAddToRecent"]
    }).then((value) => {
        let folderNames = value.filePaths;
        if (value.canceled) {
            console.log("outputFolderBtnEl-click: no output folder selected.");
            return;     // do nothing
        }
    
        let folderName = folderNames[0];

        // update DOM
        outputFolderInputEl.value = folderName;
    });
});

metadataCheckboxEl.addEventListener("change", (ev) => {
    if (ev.currentTarget.checked) {
        metadataSelectEl.disabled = false;
    } else {
        metadataSelectEl.disabled = true;
    }
})

function setAlert(msg, step = 1) {
    switch(step) {
    case 1: {
        alertMsgSpanEl.innerHTML = msg;
        alertMsgSpanEl.classList.add("animate__animated", "animate__flash");
        alertMsgSpanEl.addEventListener("animationend", () => {
            alertMsgSpanEl.classList.remove("animate__animated", "animate__flash");
        });
        break;
    }
    case 2: {
        alertMsgSpanStep2El.innerHTML = msg;
        alertMsgSpanStep2El.classList.add("animate__animated", "animate__flash");
        alertMsgSpanStep2El.addEventListener("animationend", () => {
            alertMsgSpanStep2El.classList.remove("animate__animated", "animate__flash");
        });
        break;
    }
    }
};

function removeAlert(step = 1) {
    switch(step) {
    case 1: {
        alertMsgSpanEl.innerHTML = "";
        break;
    }
    case 2: {
        alertMsgSpanStep2El.innerHTML = "";
        break;
    }
    }
    
}

function disableUIStep1() {
    startBtnEl.setAttribute("disabled", true);
    inputFolderBtnEl.setAttribute("disabled", true);
    outputFolderBtnEl.setAttribute("disabled", true);
    resourceSizeInputEl.setAttribute("disabled", true);
    collectionNameInputEl.setAttribute("disabled", true);
    countInputEl.setAttribute("disabled", true);
    metadataCheckboxEl.setAttribute("disabled", true);
    startingIndexInputEl.setAttribute("disabled", true);
    step1BtnEl.setAttribute("disabled", true);
    step2BtnEl.setAttribute("disabled", true);
}

function enableUIStep1() {
    startBtnEl.removeAttribute("disabled");
    inputFolderBtnEl.removeAttribute("disabled");
    outputFolderBtnEl.removeAttribute("disabled");
    resourceSizeInputEl.removeAttribute("disabled");
    collectionNameInputEl.removeAttribute("disabled");
    countInputEl.removeAttribute("disabled");
    metadataCheckboxEl.removeAttribute("disabled");
    startingIndexInputEl.removeAttribute("disabled");
    step1BtnEl.removeAttribute("disabled");
    step2BtnEl.removeAttribute("disabled");
}

/**
    we only check the existence of the input fields. The correctness of them will be
    checked on the server side.
*/
startBtnEl.addEventListener("click", async () => {
    disableUIStep1();
    removeAlert(1);
    // reset progress bar
    progressBarEl.classList.remove("progress-bar-striped", "progress-bar-animated", "bg-success", "bg-danger");
    progressBarEl.innerHTML = "";

    let inputFolder = inputFolderInputEl.value;
    let outputFolder = outputFolderInputEl.value;
    let resourceSize = resourceSizeInputEl.value;
    let collectionName = collectionNameInputEl.value;
    let enableMetadata = metadataCheckboxEl.checked;
    let metadataStd = metadataSelectEl.value;
    let count = countInputEl.value;
    let enableExcel = excelCheckboxEl.checked;
    let startingIndex = startingIndexInputEl.value;

    // check - inputFolder
    if (inputFolder == "" || inputFolder == undefined || inputFolder == null) {
        setAlert("请选择素材文件夹");
        enableUIStep1();
        return;
    }
    // check - outputFolder
    if (outputFolder == "" || outputFolder == undefined || outputFolder == null) {
        setAlert("请选择输出文件夹");
        enableUIStep1();
        return;
    }
    // check - resource size
    if (resourceSize <= 0 || resourceSize % 1 !== 0) {
        setAlert("请输入一个正整数作为素材尺寸");
        enableUIStep1();
        return;
    }
    // check - collectionName
    if (collectionName == "" || collectionName == undefined || collectionName == null) {
        setAlert("请输入藏品系列名称");
        enableUIStep1();
        return;
    }
    // check - count
    if (count <= 0 || count % 1 !== 0) {
        setAlert("请输入一个正整数作为藏品数量");
        enableUIStep1();
        return;
    }
    // check - starting index
    if (startingIndex <= 0 || startingIndex % 1 !== 0) {
        setAlert("请输入一个正整数作为藏品起始编号");
        enableUIStep1();
        return;
    }

    let params = {
        "context_id": "233",
        "config": {
            "path": inputFolder,
            "count": Number(count),
            "output-path": outputFolder,
            "sep": ".",
            "meta-std": metadataStd,
            "collection-name": collectionName,
            "resource-size": Number(resourceSize),
            "starting-index": Number(startingIndex)
        },
        "enable_render": true,
        "enable_metadata": enableMetadata,
        "enable_excel": enableExcel
    };
    console.log(params);

    try {
        let response = await axios.post(baseURL + "new", params);

        if (response.data.success) {
            // check progress
            let job = setInterval(() => {
                try {
                    axios.post(baseURL + "check", {"context_id": "233"}).then((jobResponse) => {
                        console.log(jobResponse.data);
                        if (jobResponse.data.success) {     // if the request success (not the NFT generation)
                            // set progress bar anyway
                            let progress = jobResponse.data.data.progress;
                            let total = jobResponse.data.data.total;
                            console.log("progress=%d total=%d", progress, total);
                            let percentage = Math.floor(progress/total*100);
                            console.log("percentage=%d", percentage);
                            progressBarEl.style.width = `${percentage}%`;
                            progressBarEl.innerHTML = `${progress}/${total}`;

                            if (jobResponse.data.data.executing) {      // if the NFT generation is still running
                                if (progress == total) {        // metadata may take some time
                                    progressBarEl.classList.add(["progress-bar-striped", "progress-bar-animated"]);
                                }
                            } else {
                                if (jobResponse.data.data.success) {        // if the NFT generation is finished successfully
                                    enableUIStep1();
                                    progressBarEl.classList.remove("progress-bar-striped", "progress-bar-animated");
                                    progressBarEl.classList.add("bg-success");
                                    progressBarEl.innerHTML += " == 执行成功";
                                } else {        // if the NFT generation failed
                                    enableUIStep1();
                                    progressBarEl.classList.remove("progress-bar-striped", "progress-bar-animated");
                                    progressBarEl.classList.add("bg-danger");
                                    progressBarEl.innerHTML += " == 执行失败";
                                    setAlert(jobResponse.data.data.error_msg);
                                }
                                clearInterval(job);
                            }
                        } else {        // if the request failed
                            setAlert(jobResponse.data.message);
                            // and do nothing, it will retry
                        }
                    });
                } catch (jobErr) {
                    console.log(jobErr);
                    // and do nothing, it will retry
                }
            }, 1000);
        } else {
            setAlert(response.data.message);
            enableUIStep1();
        }
    } catch (e) {
        setAlert(e.message);
        enableUIStep1();
    }
});

/* ----------------------------------- 第二步 ---------------------------------- */
inputFolderBtnStep2El.addEventListener("click", () => {
    remote.dialog.showOpenDialog(remote.getCurrentWindow(), {
        title: "选择第一步生成的 Excel 文件",
        buttonLabel: "选择",
        properties: ["openFile"],
        filters: [{name: "Excel 文件", extensions: ["xlsx"]}]
    }).then((value) => {
        let fileNames = value.filePaths;
        if (value.canceled) {
            console.log("inputFolderBtnStep2El-click: no Excel file selected.");
            return;     // do nothing
        }
    
        let fileName = fileNames[0];    // with filename and ext
    
        // update DOM
        inputFolderInputStep2El.value = fileName;
        outputFolderInputStep2El.value = path.dirname(fileName);      // always auto fill
    });
});

function disableUIStep2() {
    step1BtnEl.setAttribute("disabled", true);
    step2BtnEl.setAttribute("disabled", true);
    inputFolderBtnStep2El.setAttribute("disabled", true);
    deleteCheckboxStep2El.setAttribute("disabled", true);
    reorderCheckboxStep2El.setAttribute("disabled", true);
    metadataSelectStep2El.setAttribute("disabled", true);
    startBtnStep2El.setAttribute("disabled", true);
}

function enableUIStep2() {
    step1BtnEl.removeAttribute("disabled");
    step2BtnEl.removeAttribute("disabled");
    inputFolderBtnStep2El.removeAttribute("disabled");
    deleteCheckboxStep2El.removeAttribute("disabled");
    reorderCheckboxStep2El.removeAttribute("disabled");
    metadataSelectStep2El.removeAttribute("disabled");
    startBtnStep2El.removeAttribute("disabled");
}

/**
    we only check the existence of the input fields. The correctness of them will be
    checked on the server side.
*/
startBtnStep2El.addEventListener("click", async () => {
    disableUIStep2();
    removeAlert(2);

    let inputFolder = inputFolderInputStep2El.value;
    let outputFolder = outputFolderInputStep2El.value;
    let metadataStd = metadataSelectStep2El.value;
    let enableDelete = deleteCheckboxStep2El.checked;
    let enableReorder = reorderCheckboxStep2El.checked;
    let collectionName = collectionNameInputStep2El.value

    // check - inputFolder
    if (inputFolder == "" || inputFolder == undefined || inputFolder == null) {
        setAlert("请选择 Excel 文件", 2);
        enableUIStep2();
        return;
    }
    // check - outputFolder
    if (outputFolder == "" || outputFolder == undefined || outputFolder == null) {
        setAlert("请选择输出文件夹", 2);
        enableUIStep2();
        return;
    }
    // check - collection name
    if (collectionName == "" || collectionName == undefined || collectionName == null) {
        setAlert("请输入藏品名称", 2);
        enableUIStep2();
        return;
    }

    let params = {
        "config": {
            "path": inputFolder,
            "output-path": outputFolder,
            "meta-std": metadataStd,
            "collection-name": collectionName
        },
        "enable-delete": enableDelete,
        "enable-reorder": enableReorder
    };
    console.log(params);

    try {
        let response = await axios.post(baseURL + "from_excel", params);

        if (response.data.success) {
            enableUIStep2();
            setAlert("执行成功，为 " + response.data.data.count + " 个藏品生成元数据", 2);
        } else {
            setAlert("执行失败：" + response.data.message, 2);
            enableUIStep2();
        }
    } catch (e) {
        setAlert(e.message, 2);
        enableUIStep2();
    }
});

let currentStep = 1;
step2BtnEl.addEventListener("click", (ev) => {
    if (currentStep == 1) {
        step1ContainerEl.hidden = true;
        step2ContainerEl.hidden = false;
        currentStep = 2;

        // change the button style
        step1BtnEl.classList.remove("btn-primary");
        step1BtnEl.classList.add("btn-outline-primary");
        step2BtnEl.classList.remove("btn-outline-primary");
        step2BtnEl.classList.add("btn-primary");
    }
});

step1BtnEl.addEventListener("click", (ev) => {
    if (currentStep == 2) {
        step2ContainerEl.hidden = true;
        step1ContainerEl.hidden = false;
        currentStep = 1;

        // change the button style
        step1BtnEl.classList.remove("btn-outline-primary");
        step1BtnEl.classList.add("btn-primary");
        step2BtnEl.classList.remove("btn-primary");
        step2BtnEl.classList.add("btn-outline-primary");
    }
})