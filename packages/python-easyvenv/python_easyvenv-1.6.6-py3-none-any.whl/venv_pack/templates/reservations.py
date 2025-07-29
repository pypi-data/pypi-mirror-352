'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Заявки</title>
    {% load static %}
</head>
<body>
    {% include 'menu.html' %}
    <table>
        <thead>
            <tr>
                <th>Дата/Время</th>
                <th>Описание</th>
                <th>Статус</th>
            </tr>
        </thead>
        <tbody>
            {% for res in reservations %}
            <tr>
                <td>{{ res.date|date:"d.m.Y" }} {{ res.time|time:"H:i" }}</td>
                <td>{{ res.description }}</td>
                <td>
                    {{ res.get_status_display }}
                    {% if res.comment %}{{ res.comment }}{% endif %}
                </td>
            </tr>
            {% empty %}
                <tr>
                    <td colspan="3">У вас пока нет броней</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>'''