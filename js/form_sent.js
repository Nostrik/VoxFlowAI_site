document.querySelector(".contact-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    
    console.log("=== ОТПРАВКА ФОРМЫ ===");
    
    // Собираем данные
    const formData = new FormData(e.target);
    const data = {
        email: formData.get('email'),
        company: formData.get('company'),
        phone: formData.get('phone'),
        description: formData.get('description')
    };
    
    console.log("Данные для отправки:", data);
    
    // Визуальная индикация отправки (опционально)
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "Отправка...";
    submitBtn.disabled = true;
    
    try {
        console.log("Отправка запроса...");
        const response = await fetch("http://localhost:8080/form-handler", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        
        console.log("Статус ответа:", response.status);
        
        const result = await response.json();
        console.log("Тело ответа:", result);
        
        if (response.ok) {
            console.log("✅ Форма успешно отправлена!");
            e.target.reset();
            
            // Можно добавить едва заметную индикацию успеха
            submitBtn.textContent = "✓ Отправлено";
            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        } else {
            console.error("❌ Ошибка сервера:", result.message);
            submitBtn.textContent = "✗ Ошибка";
            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        }
    } catch (error) {
        console.error("Ошибка сети:", error);
        submitBtn.textContent = "✗ Ошибка сети";
        setTimeout(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }
});

// document.querySelector(".contact-form").addEventListener("submit", async (e) => {
//     e.preventDefault();
    
//     console.log("=== ОТПРАВКА ФОРМЫ ===");
    
//     // Собираем данные
//     const formData = new FormData(e.target);
//     const data = {
//         email: formData.get('email'),
//         company: formData.get('company'),
//         phone: formData.get('phone'),
//         description: formData.get('description')
//     };
    
//     console.log("Данные для отправки:", data);
    
//     try {
//         console.log("Отправка запроса...");
//         const response = await fetch("http://localhost:8080/form-handler", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify(data)
//         });
        
//         console.log("Статус ответа:", response.status);
//         console.log("Заголовки ответа:", Object.fromEntries(response.headers.entries()));
        
//         const result = await response.json();
//         console.log("Тело ответа:", result);
        
//         if (response.ok) {
//             alert("✅ Форма успешно отправлена!");
//             e.target.reset();
//         } else {
//             alert("❌ Ошибка сервера: " + (result.message || 'Неизвестная ошибка'));
//         }
//     } catch (error) {
//         console.error("Ошибка сети:", error);
//         alert("❌ Ошибка сети: " + error.message);
//     }
// });