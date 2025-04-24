document.addEventListener("DOMContentLoaded", () => {
    const burger = document.querySelector(".burger-menu");
    const panel = document.getElementById("side-panel");
    const overlay = document.getElementById("overlay");
    const closeBtn = document.querySelector(".close-btn");

    function openPanel() {
        panel.style.left = "0px";
        overlay.style.display = "block";
    }

    function closePanel() {
        panel.style.left = "-250px";
        overlay.style.display = "none";
    }

    if (burger) {
        burger.addEventListener("click", openPanel);
    }

    if (overlay) {
        overlay.addEventListener("click", closePanel);
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closePanel);
    }
});