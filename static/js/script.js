const imageInput = document.getElementById("imageInput");
const previewContainer = document.getElementById("previewContainer");
const imageCount = document.getElementById("imageCount");
const dropArea = document.getElementById("dropArea");
const premiumPopup = document.getElementById("premiumPopup");
const closePopup = document.getElementById("closePopup");

let selectedImages = [];

// ----------------------
// Update Hidden Input
// ----------------------
function updateFileInput() {

    const dataTransfer = new DataTransfer();

    selectedImages.forEach(file => {
        dataTransfer.items.add(file);
    });

    imageInput.files = dataTransfer.files;

}

// ----------------------
// Image Counter
// ----------------------
function updateCounter() {

    imageCount.textContent =
        `${selectedImages.length} Image(s) Selected`;

}

// ----------------------
// Preview Images
// ----------------------
function showPreviews() {

    previewContainer.innerHTML = "";

    updateCounter();

    selectedImages.forEach((file, index) => {

        const reader = new FileReader();

        reader.onload = function(e){

            const card = document.createElement("div");

            card.className = "preview-card";

            card.dataset.index = index;

            card.innerHTML = `
                <img src="${e.target.result}" alt="Preview">

                <button
                    class="remove-btn"
                    data-index="${index}">
                    ✖
                </button>
            `;

            previewContainer.appendChild(card);

        };

        reader.readAsDataURL(file);

    });

}

// ----------------------
// File Selection
// ----------------------
imageInput.addEventListener("change", function(){

    selectedImages = Array.from(this.files);

    if(selectedImages.length > 25){

        premiumPopup.style.display = "flex";

    }

    updateFileInput();

    showPreviews();

});

// ----------------------
// Premium Popup
// ----------------------
closePopup.onclick = function(){

    premiumPopup.style.display = "none";

    selectedImages = selectedImages.slice(0,25);

    updateFileInput();

    showPreviews();

};

// ----------------------
// Remove Image
// ----------------------
previewContainer.addEventListener("click", function(e){

    if(!e.target.classList.contains("remove-btn"))
        return;

    const index = Number(e.target.dataset.index);

    selectedImages.splice(index,1);

    updateFileInput();

    showPreviews();

});

// ----------------------
// Drag & Drop
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
        .filter(file => file.type.startsWith("image/"));

    droppedFiles.forEach(file => {

        const exists = selectedImages.some(img =>
            img.name === file.name &&
            img.size === file.size
        );

        if (!exists) {
            selectedImages.push(file);
        }

    });

    if (selectedImages.length > 25) {
        premiumPopup.style.display = "flex";
    }

    updateFileInput();
    showPreviews();

});
// ----------------------
// Sort Preview Images
// ----------------------

new Sortable(previewContainer, {

    animation: 200,

    ghostClass: "sortable-ghost",

    onEnd: function (evt) {

        const movedItem = selectedImages.splice(evt.oldIndex, 1)[0];

        selectedImages.splice(evt.newIndex, 0, movedItem);

        updateFileInput();

        showPreviews();

    }

});