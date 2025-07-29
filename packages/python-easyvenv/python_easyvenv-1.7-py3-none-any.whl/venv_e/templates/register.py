'''{% extends 'base.html' %}

{% block title %}Регистрация{% endblock %}

{% block content %}
<div class="auth-container">
    <h2>Регистрация</h2>
    <form method="post">
        {% csrf_token %}

        <div class="form-group">
            <label for="username">Логин*</label>
            <input type="text" id="username" name="username" required class="form-control">
            {% if form.username.errors %}
                <div class="error">{{ form.username.errors }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="email">Email*</label>
            <input type="email" id="email" name="email" required class="form-control">
            {% if form.email.errors %}
                <div class="error">{{ form.email.errors }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="password1">Пароль*</label>
            <input type="password" id="password1" name="password1" required class="form-control">
            {% if form.password1.errors %}
                <div class="error">{{ form.password1.errors }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="password2">Подтверждение пароля*</label>
            <input type="password" id="password2" name="password2" required class="form-control">
            {% if form.password2.errors %}
                <div class="error">{{ form.password2.errors }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="first_name">Имя*</label>
            <input type="text" id="first_name" name="first_name" required class="form-control">
        </div>

        <div class="form-group">
            <label for="last_name">Фамилия*</label>
            <input type="text" id="last_name" name="last_name" required class="form-control">
        </div>

        <div class="form-group">
            <label for="middle_name">Отчество</label>
            <input type="text" id="middle_name" name="middle_name" class="form-control">
        </div>

        <div class="form-group">
            <label for="snils">СНИЛС (11 цифр)*</label>
            <input type="text" id="snils" name="snils" pattern="\d{11}" required class="form-control">
        </div>

        <div class="form-group">
            <label for="phone">Телефон (11 цифр)*</label>
            <input type="tel" id="phone" name="phone" pattern="\d{11}" required class="form-control">
        </div>

        <div class="form-group">
            <input type="checkbox" id="gal" name="gal" required style="width: auto; display: inline-block;">
            <label for="gal" style="display: inline;">Я согласен с правилами*</label>
        </div>

        <button type="submit" class="btn">Зарегистрироваться</button>
    </form>
</div>
{% endblock %}'''