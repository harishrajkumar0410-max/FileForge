const pdfInput = document.getElementById("pdfInput");
const previewContainer = document.getElementById("previewContainer");
const pdfCount = document.getElementById("pdfCount");
const dropArea = document.getElementById("dropArea");

let selectedPDFs = [];

// ----------------------
// Update Hidden Input
// ----------------------
function updateFileInput() {

    const dataTransfer = new DataTransfer();

    selectedPDFs.forEach(file => {
        dataTransfer.items.add(file);
    });

    pdfInput.files = dataTransfer.files;

}

// ----------------------
// Update Counter
// ----------------------
function updateCounter() {

    pdfCount.textContent =
        `${selectedPDFs.length} PDF(s) Selected`;

}

// ----------------------
// Show PDF Cards
// ----------------------
function showPreviews() {

    previewContainer.innerHTML = "";

    updateCounter();

    selectedPDFs.forEach((file, index) => {

        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

        const card = document.createElement("div");

        card.className = "preview-card";

        card.innerHTML = `
    <button class="remove-btn"
            data-index="${index}">
        ✖
    </button>

    <div class="pdf-icon">
        📄
    </div>

    <h3>${file.name}</h3>

    <p>${sizeMB} MB</p>
`;

        previewContainer.appendChild(card);

    });

}

// ----------------------
// Select PDFs
// ----------------------
pdfInput.addEventListener("change", function () {

    const newFiles = Array.from(this.files);

    newFiles.forEach(file => {

        const exists = selectedPDFs.some(pdf =>
            pdf.name === file.name &&
            pdf.size === file.size
        );

        if (!exists) {
            selectedPDFs.push(file);
        }

    });

    updateFileInput();

    showPreviews();

    // Clear the input so the same file can be selected again later if needed
    //pdfInput.value = "";

});

// ----------------------
// Remove PDF
// ----------------------
previewContainer.addEventListener("click", function (e) {

    if (!e.target.classList.contains("remove-btn"))
        return;

    const index = Number(e.target.dataset.index);

    selectedPDFs.splice(index, 1);

    updateFileInput();

    showPreviews();

});

// ----------------------
// Drag & Drop PDFs
// ----------------------

["dragenter", "dragover"].forEach(eventName => {

    dropArea.addEventListener(eventName, (e) => {

        e.preventDefault();
        dropArea.classList.add("dragging");

    });

});

["dragleave", "drop"].forEach(eventName => {

    dropArea.addEventListener(eventName, (e) => {

        e.preventDefault();
        dropArea.classList.remove("dragging");

    });

});

dropArea.addEventListener("drop", (e) => {

    e.preventDefault();

    const droppedFiles = Array.from(e.dataTransfer.files)
        .filter(file => file.type === "application/pdf");

    droppedFiles.forEach(file => {

        const exists = selectedPDFs.some(pdf =>
            pdf.name === file.name &&
            pdf.size === file.size
        );

        if (!exists) {
            selectedPDFs.push(file);
        }

    });

    updateFileInput();
    showPreviews();

});

// ----------------------
// Sort PDF Cards
// ----------------------

new Sortable(previewContainer, {

    animation: 200,

    ghostClass: "sortable-ghost",

    onEnd: function (evt) {

        const movedPDF = selectedPDFs.splice(evt.oldIndex, 1)[0];

        selectedPDFs.splice(evt.newIndex, 0, movedPDF);

        updateFileInput();

        showPreviews();

    }

});