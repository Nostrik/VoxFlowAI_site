document.querySelector(".contact-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        email: e.target[0].value,
        company: e.target[1].value,
        phone: e.target[2].value,
        description: e.target[3].value
    };

    await fetch("https://http://localhost:8080/form-handler", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    alert("Отправлено!");
});