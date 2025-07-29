'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Профиль</title>
    {% load static %}
</head>
<body>
    {% include 'menu.html' %}
    <p>Email: {{ user.email }}</p>
    <p>Телефон: {{ user_profile.phone }}</p>
    <p>ФИО: {{ user_profile.FIO }}</p>

    <div>
        <button id="editProfileBtn">Редактировать</button>

        <form method="post" id="editProfileForm" style="display: none">
            {% csrf_token %}
            <div>
                {{ user_form.email.label }}:<br>
                {{ user_form.email }}
                <div class="error" id="email-error"></div>
            </div>
            <div>
                {{ profile_form.phone.label }}:<br>
                {{ profile_form.phone }}
                <div class="error" id="phone-error"></div>
            </div>
            <div>
                {{ profile_form.FIO.label }}:<br>
                {{ profile_form.FIO }}
                <div class="error" id="FIO-error"></div>
            </div>
            <button type="submit">Сохранить</button>
        </form>
    </div>

    <script>
        document.getElementById("editProfileBtn").addEventListener("click", function() {
            document.getElementById("editProfileForm").style.display = "block";
            document.getElementById("editProfileBtn").style.display = "none";
        });
    </script>
</body>
</html>'''