'''{% extends 'base.html' %}

{% block content %}
<div class="direction-card">
            <div class="direction-code">{{ naprav.cod }}</div>
            <h3 class="direction-name">{{ naprav.name }}</h3>
            <p><strong>Область:</strong> {{ naprav.obl }}</p>
            <p><strong>Срок обучения:</strong> {{ naprav.year }}</p>
            <p><strong>Бюджетные места:</strong> {{ naprav.budget }}</p>
        <a href="{% url 'catalog' %}" class="nav-detail">Обратно</a>
        {% if user.is_authenticated %}
        <div class="application-form">
         {% if user.is_authenticated %}
        <form method="post">
            {% csrf_token %}
            <button type="submit" class="btn-apply">
                <i class="fas fa-paper-plane"></i> Подать заявку
            </button>
        </form>
        {% else %}
        <div class="login-prompt">
            <p>Чтобы подать заявку, <a href="{% url 'login' %}">войдите в систему</a> или <a href="{% url 'register' %}">зарегистрируйтесь</a>.</p>
        </div>
    {% endif %}
</div>
    {% else %}
        <p>Чтобы подать заявку, <a href="{% url 'login' %}">войдите</a>.</p>
    {% endif %}
</div>

{% endblock %}'''