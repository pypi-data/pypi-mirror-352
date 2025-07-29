'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Регистрация</title>
    {% load static %}
</head>
<body>
    {% include 'menu.html' %}
    <form method="POST" action="" id="registration-form">
        {% csrf_token %}
        <div>
            <label for="id_username">Логин</label>
            {{ user_form.username }}
            <div id="username-error"></div>
        </div>
        <div>
            <label for="id_FIO">{{ profile_form.FIO.label }}</label>
            {{ profile_form.FIO }}
            <div id="FIO-error"></div>
        </div>
        <div>
            <label for="id_phone">{{ profile_form.phone.label }}</label>
            {{ profile_form.phone }}
            <div id="phone-error"></div>
        </div>
        <div>
            <label for="id_email">Email</label>
            {{ user_form.email }}
            <div id="email-error"></div>
        </div>
        <div>
            <label for="id_password1">Пароль</label>
            {{ user_form.password1 }}
            <div id="password1-error"></div>
        </div>
        <div>
            <label for="id_password2">Подтверждение пароля</label>
            {{ user_form.password2 }}
            <div id="password2-error"></div>
        </div>

        <button name="CreateUser">Зарегистрироваться</button>
        <div>
            Уже есть аккаунт? <a href="{% url 'login' %}">Войти</a>
        </div>
    </form>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
        const phoneField = document.getElementById('id_phone');
        if (phoneField) {
            phoneField.addEventListener('input', function(e) {
                const x = e.target.value.replace(/\D/g, '').match(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
                e.target.value = !x[2] ? '+7' : `+7(${x[2]}${x[3] ? `)${x[3]}` : ''}${x[4] ? `-${x[4]}` : ''}${x[5] ? `-${x[5]}` : ''}`;
            });
        }

        document.getElementById('registration-form').addEventListener('submit', function(event) {
            let isValid = true;
            const namePattern = /^[а-яА-ЯёЁ\s]+$/;
            const usernamePattern = /^[a-zA-Z0-9\s\-]+$/;
            const phonePattern = /^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$/;
            const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;

            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

            const password1 = document.getElementById('id_password1');
            if (!passwordPattern.test(password1.value)) {
                password1.classList.add('is-invalid');
                document.getElementById('password1-error').textContent =
                    'Пароль должен содержать минимум 8 символов, включая буквы и цифры';
                isValid = false;
            }

            const FIO = document.getElementById('id_FIO');
            if (!namePattern.test(FIO.value.trim())) {
                FIO.classList.add('is-invalid');
                document.getElementById('FIO-error').textContent = 'ФИО может содержать только кириллицу и пробелы';
                isValid = false;
            }

            const phone = document.getElementById('id_phone');
            if (!phonePattern.test(phone.value.trim())) {
                phone.classList.add('is-invalid');
                document.getElementById('phone-error').textContent = 'Номер телефона должен соответствовать формату +7(XXX)-XXX-XX-XX';
                isValid = false;
            }

            const username = document.getElementById('id_username');
            if (!usernamePattern.test(username.value.trim())) {
                username.classList.add('is-invalid');
                document.getElementById('username-error').textContent = 'Логин может содержать только латиницу, цифры, пробелы и тире';
                isValid = false;
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    </script>
</body>
</html>'''