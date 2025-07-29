'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ product.name }}</title>
    {% load static %}
</head>
<body>
    {% include 'menu.html' %}
    {{ product.name }}
    {% if product.image %}
        <img src="{{ product.image.url }}" alt="{{ product.name }}">
    {% endif %}
</body>
</html>'''