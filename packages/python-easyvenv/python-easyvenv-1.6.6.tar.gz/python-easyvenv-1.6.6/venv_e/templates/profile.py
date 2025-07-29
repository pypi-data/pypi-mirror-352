'''{% extends 'base.html' %}

{% block title %}Профиль{% endblock %}

{% block content %}
<div class="auth-container">
    <h2>Ваш профиль</h2>

    <div class="profile-info">
        <p><strong>Имя:</strong> {{ user.first_name }}</p>
        <p><strong>Фамилия:</strong> {{ user.last_name }}</p>
        <p><strong>Отчество:</strong> {{ user.middle_name }}</p>
        <p><strong>Логин:</strong> {{ user.username }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Телефон:</strong> {{ user.phone }}</p>
        <p><strong>СНИЛС:</strong> {{ user.snils }}</p>
    </div>
</div>
{% endblock %}'''