'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Авторизация</title>
    {% load static %}
</head>
<body>
    {% include 'menu.html' %}
    <div>
        <form method="POST" id="auth-form">
            {% csrf_token %}
            <p>АВТОРИЗАЦИЯ</p>
            <div>
                <label for="id_username">{{ form.username.label }}</label>
                {{ form.username }}
                <div class="error" id="username-error-auth"></div>
            </div>
            <div>
                <label for="id_password">{{ form.password.label }}</label>
                {{ form.password }}
            </div>
            <button type="submit">ВОЙТИ</button>
            <div>Ещё не зарегистрированы?<br><a href="{% url 'registration' %}">Зарегистрироваться</a></div>
        </form>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('auth-form').addEventListener('submit', function(event) {
                event.preventDefault();

                document.querySelectorAll('.error').forEach(el => el.textContent = '');

                let isValid = true;

                const usernamePattern = /^[a-zA-Z0-9\s\-]+$/;
                const username = document.getElementById('id_username').value.trim();

                if (!usernamePattern.test(username)) {
                    document.getElementById('username-error-auth').textContent = 'Логин может содержать только латиницу, цифры, пробелы и тире.';
                    isValid = false;
                }

                if (isValid) {
                    this.submit();
                }
            });
        });
    </script>
</body>
</html>'''