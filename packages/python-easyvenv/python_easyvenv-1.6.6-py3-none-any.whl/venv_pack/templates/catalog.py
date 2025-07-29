'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Каталог</title>
</head>
<body>
    {% include 'menu.html' %}
    <div>
        <h2>Сортировка</h2>
        <ul>
            <li><a href="?sort=name">По названию</a></li>
            <li><a href="?sort=price">По цене</a></li>
            <li><a href="?sort=">Без сортировки</a></li>
        </ul>
    </div>
    {% for product in catalog %}
        <div>
            {% if product.image %}
                <img src="{{ product.image.url }}" alt="{{ product.name }}">
            {% endif %}
            <a href="{% url 'catalog_detail' product.id %}">{{ product.name }}</a>
        </div>
    {% empty %}
        <p>В данный момент нет доступных товаров</p>
    {% endfor %}
    <article class="pagination">
        <span class="step-links">
            {% if catalog.has_previous %}
                <a href="?page=1">&laquo; Первая</a>
                <a href="?page={{ catalog.previous_page_number }}">Предыдущая</a>
            {% endif %}

            <span class="current">
                Страница {{ catalog.number }} из {{ catalog.paginator.num_pages }}.
            </span>

            {% if catalog.has_next %}
                <a href="?page={{ catalog.next_page_number }}">Следующая</a>
                <a href="?page={{ catalog.paginator.num_pages }}">Последняя &raquo;</a>
            {% endif %}
        </span>
    </article>
</body>
</html>'''