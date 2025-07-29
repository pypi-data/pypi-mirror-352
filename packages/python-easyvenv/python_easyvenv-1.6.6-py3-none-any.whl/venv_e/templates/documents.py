'''{% extends 'base.html' %}

{% load static %}
{% block content %}
<div class="zag">
    <h1>Документы нашей учебной организации</h1>

    <ul>
        <li>
            <a href="{% static 'documents/pdf1.pdf' %}">Лицензия организации</a>
        </li>
    </ul>
</div>
{% endblock %}'''