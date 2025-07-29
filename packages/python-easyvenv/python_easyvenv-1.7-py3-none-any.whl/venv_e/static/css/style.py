'''        * {
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        body {
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            color: white;
        }
        .nav-links {
            display: flex;
            gap: 1.5rem;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background-color: #34495e;
        }
        .btn-logout {
            background-color: #e74c3c;
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn-logout:hover {
            background-color: #c0392b;
        }
        .auth-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }
        .btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .error {
            color: #e74c3c;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }

        .directions-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            padding: 20px;
        }
        .direction-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .direction-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .direction-code {
            font-weight: bold;
            color: #2c3e50;
        }
        .direction-name {
            font-size: 1.2em;
            margin: 10px 0;
            color: #3498db;
        }

        .zag{
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-detail {
            color: white;
            background-color: #34495e;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav-detail:hover {
            background-color: #34495e;
        }
            /* Стили для формы заявки */
    .application-form {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }

    .btn-apply {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        display: inline-block;
        margin-top: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .btn-apply:hover {
        background-color: #2ecc71;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .btn-apply:active {
        transform: translateY(0);
    }

    .login-prompt {
        margin-top: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 4px;
        border-left: 4px solid #3498db;
    }

    .login-prompt a {
        color: #3498db;
        font-weight: 600;
        text-decoration: none;
    }

    .login-prompt a:hover {
        text-decoration: underline;
    }


    .success-message {
        animation: fadeIn 0.5s ease;
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 4px;
        margin-top: 20px;
        border-left: 4px solid #28a745;
    }
'''