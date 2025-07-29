'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header class="header">
        <a href="{% url 'index' %}" class="logo">МойСайт</a>
        <a href="{% url 'catalog' %}" class="nav-link"> Напрвления</a>
        <a href="{% url 'documents' %}" class="nav-link">Документы</a>
        <div class="nav-links">
            {% if user.is_authenticated %}
                <a href="{% url 'profile' %}" class="nav-link">Профиль</a>
                <form action="{% url 'logout' %}" method="post" style="display: inline;">
                    {% csrf_token %}
                    <button type="submit" class="btn-logout">Выйти</button>
                </form>
            {% else %}
                <a href="{% url 'login' %}" class="nav-link">Войти</a>
                <a href="{% url 'register' %}" class="nav-link">Регистрация</a>
            {% endif %}
        </div>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>'''