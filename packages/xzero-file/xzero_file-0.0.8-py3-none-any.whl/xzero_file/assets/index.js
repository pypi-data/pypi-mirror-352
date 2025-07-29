const fileListElement = document.getElementById("file-list")
const submitUploadFileElement = document.getElementById("btn-submit-upload-file")
const fileInputElement = document.getElementById("file-input")
const uploadStatusElement = document.getElementById("upload-status")

let basePath="."
let fileIcon=""
let dirIcon=""

async function loadSVG(name) {
    try {
        const response = await fetch(`/assets/images/${name}.svg`);
        if (!response.ok) {
            throw new Error('Failed to load SVG');
        }
        const svgText = await response.text();
        return svgText;
    } catch (error) {
        console.error('Error loading SVG:', error);
    }
}

async function fetchFileList(name) {
    try {
        const searchParams = new URLSearchParams({name: name})
        const response = await fetch(`/api/files?${searchParams.toString()}`); // Replace with your API endpoint
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fileList = await response.json();
        return fileList
    } catch (error) {
        console.error("Could not fetch file list:", error);
    }
}

async function displayFileList(base, files) {
    fileListElement.innerHTML = "";
    files.forEach(async (file) => {
        const fileItemElement = document.createElement("div")
        fileItemElement.className = "file-item"
        
        const link = document.createElement("a");
        link.href="#";
        const iconElement = document.createElement("div");
        iconElement.className="file-type-icon"
        if (file.is_dir) {
            iconElement.innerHTML = dirIcon;
            link.textContent = `${file.name}`
        } else {
            iconElement.innerHTML = fileIcon;
            link.textContent = `${file.name}`;
        }
        link.addEventListener("click", async function(event) {
            event.preventDefault();
            const newBase = base + "/" + file.name
            if (file.is_dir) {
                basePath = newBase;
                const file_list = await fetchFileList(newBase);
                await displayFileList(newBase, file_list.files);
            } else {
                // download
                const searchParams = new URLSearchParams({name: newBase});
                window.open(`/api/download?${searchParams.toString()}`, "_blank");
            }
        });

        fileItemElement.append(iconElement)
        fileItemElement.append(link)

        fileListElement.appendChild(fileItemElement);
    });
}

async function uploadFile() {
    uploadStatusElement.textContent = "";
    // Get the file input and status element
    const file = fileInputElement.files[0];

    // Check if a file is selected
    if (!file) {
        uploadStatusElement.textContent = "Error: Please select a file to upload.";
        return;
    }

    console.log(`select file, base name: ${basePath}, file name: ${file.name}`);
    // Display uploading status
    uploadStatusElement.textContent = "Uploading...";

    // Get the file stream
    // const stream = file.stream(); // ReadableStream for chunked upload

    let fPath = `${basePath}/${file.name}`
    try {
        // Send the file via Fetch API
        const p = new URLSearchParams({filename: fPath});
        const response = await fetch(`/api/files?${p.toString()}`, {
            method: "PUT",
            headers: {
                 "Content-Type": file.type || "application/octet-stream" // Set MIME type
            },
            body: file,
            // duplex: "half"
        });

        let r = await response.json();
        // Check response
        if (response.ok) {
            uploadStatusElement.textContent = "Success: File uploaded! " + r.file;
        } else {
            uploadStatusElement.textContent = `Error: Upload failed - ${response.status} ${r.error}`;
        }
    } catch (error) {
        uploadStatusElement.textContent = "Error: " + error.message;
        console.error("Upload error:", error);
    }
    await show_file_by_path(basePath);
}

async function show_file_by_path(p) {
    const fileList = await fetchFileList(p);
    await displayFileList(p, fileList.files);
}

async function initIcon() {
    fileIcon = await loadSVG("file");
    dirIcon = await loadSVG("dir");
}

async function init() {
    await initIcon();
    submitUploadFileElement.addEventListener("click", uploadFile);
    await show_file_by_path(".")
}
// Fetch the file list when the page loads
window.onload = init;