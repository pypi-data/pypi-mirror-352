'''{% extends 'base.html' %}
{% block content %}
    <div class="zag">
      <h1>Каталог направлений обучения</h1>
    </div>
    <div class="directions-grid">
        {% for naprav in naprav_list %}
        <div class="direction-card">
            <div class="direction-code">{{ naprav.cod }}</div>
            <h3 class="direction-name">{{ naprav.name }}</h3>
            <p><strong>Область:</strong> {{ naprav.obl }}</p>
            <p><strong>Срок обучения:</strong> {{ naprav.year }}</p>
            <p><strong>Бюджетные места:</strong> {{ naprav.budget }}</p>
            <a href="{% url 'naprav_detail' naprav.pk %}" class="nav-detail">Подробнее</a>
        </div>
        {% endfor %}
    </div>
{% endblock %}'''