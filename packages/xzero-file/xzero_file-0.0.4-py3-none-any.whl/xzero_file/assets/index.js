const fileListElement = document.getElementById("file-list")
const submitUploadFileElement = document.getElementById("btn-submit-upload-file")
const fileInputElement = document.getElementById("file-input")
const uploadStatusElement = document.getElementById("upload-status")

let basePath="."

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
    const body = document.body;
    fileListElement.innerHTML = "";
    files.forEach(async (file) => {
        const link = document.createElement("a");
        link.href="#"
        if (file.is_dir) {
            link.textContent = `[ dir  ] ${file.name}`
        } else {
            link.textContent = `[ file ] ${file.name}`;
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
        fileListElement.appendChild(link);
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

async function init() {
    submitUploadFileElement.addEventListener("click", uploadFile);
    await show_file_by_path(".")
}
// Fetch the file list when the page loads
window.onload = init;