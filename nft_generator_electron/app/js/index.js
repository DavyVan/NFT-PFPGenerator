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
let collectionNameInputEl = document.getElementById("collection-name-input");
let metadataSelectEl = document.getElementById("metadata-std-select");
let countInputEl = document.getElementById("count-input");
let progressBarEl = document.getElementById("progress-bar");
let startBtnEl = document.getElementById("start-button");
let serverStatusSpinnerEl = document.getElementById("server-status-spinner");
let serverStatusSpanEl = document.getElementById("server-status-span");
let alertMsgSpanEl = document.getElementById("alert-msg-span");


/* ------------------------------- NFGT Server ------------------------------ */

setInterval(() => {
    try {
        axios.get(baseURL + "ping").then((response) => {
            // console.log("index: NFGT Server is running. pid: %d", response.data.data.pid);
            ipcRenderer.invoke("pid", response.data.data.pid);
            overlayDivEl.hidden = true;
            serverStatusSpinnerEl.classList.remove("text-danger");
            serverStatusSpinnerEl.classList.add("text-success");
            serverStatusSpanEl.innerHTML = "图像处理服务运行中";
        });
    } catch (error) {
        serverStatusSpinnerEl.classList.remove("text-success");
        serverStatusSpinnerEl.classList.add("text-danger");
        serverStatusSpanEl.innerHTML = "图像处理服务状态未知";
    }
}, 5*1000);


/* -------------------------------- Listeners ------------------------------- */

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

function setAlert(msg) {
    alertMsgSpanEl.innerHTML = msg;
    alertMsgSpanEl.classList.add("animate__animated", "animate__flash");
    alertMsgSpanEl.addEventListener("animationend", () => {
        alertMsgSpanEl.classList.remove("animate__animated", "animate__flash");
    });
};

function removeAlert() {
    alertMsgSpanEl.innerHTML = "";
}

/**
    we only check the existence of the input fields. The correctness of them will be
    checked on the server side.
*/
startBtnEl.addEventListener("click", async () => {
    startBtnEl.setAttribute("disabled", true);
    // reset progress bar
    progressBarEl.classList.remove("progress-bar-striped", "progress-bar-animated", "bg-success", "bg-danger");
    progressBarEl.innerHTML = "";

    let inputFolder = inputFolderInputEl.value;
    let outputFolder = outputFolderInputEl.value;
    let collectionName = collectionNameInputEl.value;
    let metadataStd = metadataSelectEl.value;
    let count = countInputEl.value;

    // check - inputFolder
    if (inputFolder == "" || inputFolder == undefined || inputFolder == null) {
        setAlert("请选择素材文件夹");
        
        return;
    }
    // check - outputFolder
    if (outputFolder == "" || outputFolder == undefined || outputFolder == null) {
        setAlert("请选择输出文件夹");
        return;
    }
    // check - collectionName
    if (collectionName == "" || collectionName == undefined || collectionName == null) {
        setAlert("请输入藏品系列名称");
        return;
    }
    // check - metadataStd
    let enableMetadata = (metadataStd != "none" ? true : false);
    metadataStd = (metadataStd == "enjin" ? "enjin" : "opensea");
    // check - count
    if (count <= 0 || count % 1 !== 0) {
        setAlert("请输入一个正整数作为藏品数量");
        return;
    }
    console.log("input check pass");
    console.log(inputFolder);
    console.log(outputFolder);
    console.log(collectionName);
    console.log("%s %s", enableMetadata, metadataStd);
    console.log(count);

    try {
        let response = await axios.post(baseURL + "new", {
            "context_id": "233",
            "config": {
                "path": inputFolder,
                "count": Number(count),
                "output-path": outputFolder,
                "sep": ".",
                "meta-std": metadataStd,
                "collection-name": collectionName
            },
            "enable_render": true,
            "enable_metadata": enableMetadata
        });

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
                                    startBtnEl.removeAttribute("disabled");
                                    progressBarEl.classList.remove("progress-bar-striped", "progress-bar-animated");
                                    progressBarEl.classList.add("bg-success");
                                    progressBarEl.innerHTML += " == 执行成功";
                                } else {        // if the NFT generation failed
                                    startBtnEl.removeAttribute("disabled");
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
            startBtnEl.removeAttribute("disabled");
        }
    } catch (e) {
        setAlert(e.message);
        startBtnEl.removeAttribute("disabled");
    }
});
