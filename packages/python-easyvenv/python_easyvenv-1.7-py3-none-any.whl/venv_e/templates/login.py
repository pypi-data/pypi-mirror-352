'''{% extends 'base.html' %}

{% block title %}Вход{% endblock %}

{% block content %}
<div class="auth-container">
    <h2>Вход</h2>
    <form method="post">
        {% csrf_token %}

        <div class="form-group">
            <label for="username">Логин или Email*</label>
            <input type="text" id="username" name="username" required class="form-control">
            {% if form.username.errors %}
                <div class="error">{{ form.username.errors }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="password">Пароль*</label>
            <input type="password" id="password" name="password" required class="form-control">
            {% if form.password.errors %}
                <div class="error">{{ form.password.errors }}</div>
            {% endif %}
        </div>

        <button type="submit" class="btn">Войти</button>
    </form>
</div>
{% endblock %}'''