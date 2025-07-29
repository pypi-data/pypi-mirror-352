'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Главная</title>
    <style>
        #slider {
            position: absolute;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            z-index: 4;
        }

        #slides {
            display: flex;
            transition: transform 1s ease-in-out;
            height: 100%;
        }

        .slider-image {
            min-width: 100%;
            height: 100%;
            object-fit: cover;
        }
    </style>
</head>
<body>
    {% include 'menu.html' %}
    <div id="slider">
        <div id="slides">
            <img class="slider-image" src="{% static "images/slider1.jpg" %}" alt="фото 1">
            <img class="slider-image" src="{% static "images/slider2.jpg" %}" alt="фото 2">
            <img class="slider-image" src="{% static "images/slider3.jpg" %}" alt="фото 3">
        </div>
    </div>
    <script>
        const slides = document.querySelector('#slides');
        const totalSlides = document.querySelectorAll('.slider-image').length;
        let index = 0;
        let direction = 1;

        function changeSlide() {
            index += direction;

            if (index === totalSlides - 1) {
                direction = -1;
            } else if (index === 0) {
                direction = 1;
            }

            const offset = index * -100;
            slides.style.transform = `translateX(${offset}%)`;
        }

        setInterval(changeSlide, 3000);
    </script>
</body>
</html>
'''