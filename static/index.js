document.body.style.height = String(window.innerHeight*0.92)+"px";

const selectElement = document.getElementById("file_picker");
const result = document.getElementById("files_list");

const text = '';

selectElement.addEventListener("change", (event) => {
    const length = `${event.target.value}`.split('\\').length
    result.innerHTML = "Selected file is: "+`${event.target.value}`.split('\\')[length-1];
});


