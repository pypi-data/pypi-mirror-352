'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Создание заявки</title>
</head>
<body>
    {% include 'menu.html' %}
    <form method="post" >
        {% csrf_token %}
        <div>
            <label for="id_phone">{{ form.phone.label }}</label>
            {{ form.phone }}
        </div>
        <div>
            <label for="id_date">{{ form.date.label }}</label>
            {{ form.date }}
        </div>
        <div>
            <label for="id_time">{{ form.time.label }}</label>
            {{ form.time }}
        </div>
        <div>
            <label for="id_description">{{ form.description.label }}</label>
            {{ form.description }}
        </div>
        <button>Создать бронь</button>
    </form>
</body>
</html>'''