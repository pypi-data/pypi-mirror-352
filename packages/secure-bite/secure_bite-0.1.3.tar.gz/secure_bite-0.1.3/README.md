#   SecureBite

    SecureBite is a Django package designed to enhance authentication and session management by integrating cookie-based authentication with JWT tokens. [cite: 1, 2] It leverages Django REST Framework (DRF) and SimpleJWT to provide a secure and efficient authentication mechanism. [cite: 2]

##   Features

* **Cookie-Based Authentication** – Stores JWT tokens in HTTP-only cookies, preventing client-side access and reducing security risks. [cite: 3]

* **JWT Integration** – Uses JWT tokens for stateless authentication, ensuring efficient session management. [cite: 4]

* **Automatic Token Refreshing** – Middleware automatically refreshes tokens, maintaining seamless user sessions. [cite: 5]

* **Logout Support** – Provides a secure logout mechanism by clearing authentication cookies. [cite: 6]

##   Installation

    To integrate SecureBite into your Django project, follow these steps:

1.  **Install Required Packages**

    Run the following command:

    ```bash
    pip install rest_framework
    pip install djangorestframework-simplejwt
    pip install djangorestframework-simplejwt[token_blacklist]
    pip install secure_bite
    ```

2.  **Update Django Settings**

    In your `settings.py`, add the following configurations:

    ```python
    from datetime import timedelta

    INSTALLED_APPS = [
        'secure_bite',
        'rest_framework',
        'rest_framework_simplejwt',
        'rest_framework_simplejwt.token_blacklist',
        'corsheaders',  # Ensure CORS support
        ...
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        ...
        'secure_bite.middleware.RefreshTokenMiddleware',  # SecureBite middleware
    ]

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
    }

    JWT_AUTH_COOKIE_SETTINGS = {
        "AUTH_COOKIE": "authToken",                 # Access token cookie name
        "REFRESH_COOKIE": "refreshToken",           # Refresh token cookie name
        "AUTH_COOKIE_HTTP_ONLY": True,              # Prevents JavaScript access
        "AUTH_COOKIE_SECURE": False,                 # Use True in production (HTTPS)
        "AUTH_COOKIE_SAMESITE": "Lax",              # Or 'Strict' or 'None'
        "AUTH_COOKIE_PATH": "/",                    # Path scope of the cookie
        "USER_SERIALIZER": "secure_bite.serializers.UserSerializer"
    }

    ```

3.  **Configure URLs**

    In your root project `urls.py`, include the SecureBite authentication endpoints:

    ```python
    from django.urls import path, include

    urlpatterns = [
        ..........................
        path('auth/', include('secure_bite.urls', namespace="secure_bite")),
        ..........................
    ]
    ```

    In your `urls.py`, include the SecureBite authentication endpoints:

    ```python
    from django.urls import path, include
    from rest_framework.routers import DefaultRouter
    from secure_bite import views

    app_name = "secure_bite"

    router = DefaultRouter()
    router.register(r'auth', views.AuthenticationViewset, basename='auth')

    urlpatterns = [
        path('', include(router.urls)),
    ]
    ```

##   Usage

1.  **Login (POST /auth/login/)**

    Authenticates the user using the configured USERNAME\_FIELD (email, username, etc.) and sets the access token and refresh token in HTTP-only cookies. [cite: 9, 10]

    **Request:**

    ```json
    <!-- user_field == USERNAME_FIELD -->
    {
      "user_field": "user@example.com",
      "password": "your_password"
    }
    ```

    **Response:**

    ```json
    {
      "message": "Login successful"
    }
    ```

    **Cookies Set:**

    * `accessToken` → Contains the JWT access token (HTTP-only, Secure)

    * `refreshToken` → Contains the JWT refresh token (HTTP-only, Secure)

2.  **Logout (POST /auth/logout/)**

    Clears authentication cookies to log the user out securely. [cite: 10, 11]

    **Request:**

    ```json
    {}
    ```

    **Response:**

    ```json
    {
      "message": "Logged out"
    }
    ```

    **Cookies Cleared:**

    * `accessToken` → Deleted

    * `refreshToken` → Deleted

3.  **Get User Details (GET /auth/me/)**

    Returns the authenticated user's details. [cite: 11, 12] The access token is required in the request cookies. [cite: 12]

    **Request (Cookies must contain accessToken)**

    ```
    GET /auth/me/
    ```

    **Response (Example for custom token claims):**

    ```json
    {
      "email": "user@example.com"
    }
    ```

    **Response (If TokenObtainPairSerializer returns empty data, id is included manually):**

    ```json
    {
      "id": 1
    }
    ```

##   Automatic Token Refreshing

    SecureBite’s middleware automatically refreshes tokens. [cite: 12, 13] If an access token is about to expire, a new token is issued transparently via cookies without requiring the user to log in again. [cite: 13]

##   Security Considerations

* **Use HTTPS** – SecureBite relies on HTTP-only cookies, which require HTTPS to be fully secure. [cite: 14]

* **Enable CSRF Protection** – Ensure CSRF protection is enabled to prevent cross-site request forgery attacks. [cite: 15]

* **Token Blacklisting** – Enable token blacklisting to invalidate refresh tokens when necessary. [cite: 16]

##   React Components and Context API Example

    Here's how you might use React components and the Context API to manage the user state obtained from the `/api/user/` endpoint.

**1.  UserContext.js**

    ```jsx
    import React, { createContext, useState, useEffect, useContext } from 'react';
    import axios from 'axios'; // You'll need to install axios: npm install axios

    const UserContext = createContext();

    export const UserProvider = ({ children }) => {
      const [user, setUser] = useState(null);
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        const fetchUser = async () => {
          try {
            const response = await axios.get('/auth/me/'); // SecureBite endpoint
            setUser(response.data);
          } catch (error) {
            console.error('Error fetching user:', error);
            setUser(null); // Or handle error state appropriately
          } finally {
            setLoading(false);
          }
        };

        fetchUser();
      }, []); // Run only on mount (assumes token is already in cookies)

      const contextValue = {
        user,
        setUser,
        loading,
      };

      return (
        <UserContext.Provider value={contextValue}>
          {!loading && children} {/* Only render children if not loading */}
          {loading && <div>Loading...</div>} {/* Optional: Display a loading message */}
        </UserContext.Provider>
      );
    };

    export const useUser = () => {
      const context = useContext(UserContext);
      if (!context) {
        throw new Error('useUser must be used within a UserProvider');
      }
      return context;
    };
    ```

**2.  Example Component (Profile.js)**

    ```jsx
    import React from 'react';
    import { useUser } from './UserContext';

    const Profile = () => {
      const { user, loading } = useUser();

      if (loading) {
        return <div>Loading user data...</div>;
      }

      if (!user) {
        return <div>Not logged in or error fetching user.</div>;
      }

      return (
        <div>
          <h2>User Profile</h2>
          <p>Email: {user.email || 'N/A'}</p>
          <p>ID: {user.id || 'N/A'}</p>
          {/* Add other user details here */}
        </div>
      );
    };

    export default Profile;
    ```

**3.  Wrapping Your App**

    ```jsx
    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import App from './App';
    import { UserProvider } from './UserContext';

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
      <React.StrictMode>
        <UserProvider>
          <App />
        </UserProvider>
      </React.StrictMode>
    );
    ```

**Explanation of React Code:**

* **`UserContext`**: This context stores the user's data (`user`), a function to update it (`setUser`), and a loading state (`loading`).

* **`UserProvider`**: This component wraps your application and makes the user data available to all components that need it. It fetches the user data from `/api/user/` when it mounts. **Important:** This assumes your access token is already correctly stored in cookies by SecureBite. It also conditionally renders its children, showing a loading indicator until the user data is fetched.

* **`useUser`**: A custom hook to easily access the user context values in any component.

* **`Profile` Component**: A simple example of a component that consumes the `user` data from the context. It displays the user's email and ID (or "N/A" if not available) and handles loading and error states.

* **Wrapping `App`**: The `UserProvider` wraps the `<App />` component, making the context available throughout the application.

**Key Considerations:**

* **Error Handling**: The example includes basic error handling, but you'll likely want more robust error reporting (e.g., displaying error messages to the user).

* **Authentication Flow**: This example focuses on *fetching* the user data *after* authentication. You'll still need components and logic for the login process (using `/api/token/login/`) and logout (using `/api/token/logout/`) to set and clear the cookies, respectively.

* **axios**: You'll need to install `axios` (or use `fetch`) to make HTTP requests from your React application.

* **Security**: Always handle authentication tokens securely in your frontend code. SecureBite's cookie-based approach helps, but be mindful of XSS vulnerabilities.

* **Token Refresh**: The React code doesn't explicitly handle token refresh. SecureBite's middleware handles that on the server-side. Your React app should be designed to handle 401 Unauthorized errors gracefully, knowing that SecureBite will attempt to refresh the token behind the scenes.

* **CORS**: Ensure your Django backend is properly configured for CORS to allow requests from your React frontend.

##   Contributing

    We welcome contributions! [cite: 16, 17] To contribute:

1.  Fork the repository

2.  Create a new branch (`git checkout -b feature-branch`)

3.  Commit your changes (`git commit -m "Add new feature"`)

4.  Push to the branch (`git push origin feature-branch`)

5.  Open a pull request

##   License

    This project is licensed under the MIT License. [cite: 17, 18] See LICENSE for details.

##   Contact

    For any questions or issues, feel free to open an issue on GitHub or reach out to the maintainers.