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
        const response = await fetch("http://88.210.53.86:8080/form-handler", {
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

// document.addEventListener('DOMContentLoaded', function() {
//     console.log("DOM загружен, форма готова");
    
//     document.querySelector(".contact-form").addEventListener("submit", async (e) => {
//         e.preventDefault();
//         e.stopPropagation();
        
//         console.log("=== ОТПРАВКА ФОРМЫ ===");
        
//         // Собираем данные
//         const form = e.target;
//         const data = {
//             email: form.querySelector('[name="email"]').value,
//             company: form.querySelector('[name="company"]').value,
//             phone: form.querySelector('[name="phone"]').value,
//             description: form.querySelector('[name="description"]').value
//         };
        
//         console.log("Данные для отправки:", data);
        
//         // Проверяем, что поля заполнены
//         if (!data.email || !data.company || !data.phone || !data.description) {
//             console.error("Ошибка: заполните все поля формы!");
//             // Показываем какие поля пустые
//             if (!data.email) console.error(" - Email пустой");
//             if (!data.company) console.error(" - Компания пустая");
//             if (!data.phone) console.error(" - Телефон пустой");
//             if (!data.description) console.error(" - Описание пустое");
//             return;
//         }
        
//         const submitBtn = form.querySelector('button[type="submit"]');
//         const originalText = submitBtn.textContent;
//         submitBtn.textContent = "Отправка...";
//         submitBtn.disabled = true;
        
//         try {
//             console.log("Отправка запроса...");
//             const response = await fetch("http://localhost:8080/form-handler", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json"
//                 },
//                 body: JSON.stringify(data)
//             });
            
//             console.log("Статус ответа:", response.status);
            
//             if (response.ok) {
//                 const result = await response.json();
//                 console.log("Ответ сервера:", result);
//                 console.log("✅ Форма успешно отправлена!");
                
//                 // Очищаем форму только после успешной отправки
//                 form.reset();
                
//                 submitBtn.textContent = "✓ Отправлено";
//                 setTimeout(() => {
//                     submitBtn.textContent = originalText;
//                     submitBtn.disabled = false;
//                 }, 2000);
//             } else {
//                 console.error("❌ Ошибка сервера");
//                 submitBtn.textContent = "✗ Ошибка";
//                 setTimeout(() => {
//                     submitBtn.textContent = originalText;
//                     submitBtn.disabled = false;
//                 }, 2000);
//             }
//         } catch (error) {
//             console.error("Ошибка сети:", error);
//             submitBtn.textContent = "✗ Ошибка сети";
//             setTimeout(() => {
//                 submitBtn.textContent = originalText;
//                 submitBtn.disabled = false;
//             }, 2000);
//         }
//     });
// });