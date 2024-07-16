import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import H2PCSim from '/H2PCSS.png'; // Adjust the path as needed
import { Link } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const navigate = useNavigate();

    const handleUsernameChange = (e) => {
        setUsername(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/api/login', {
                username,
                password
            });

            console.log('Login successful:', response.data);
            localStorage.setItem('userId', response.data.userID);
            navigate('/home');
            // Handle successful login here (e.g., store token, redirect)
        } catch (error) {
            console.error('Login error:', error.response ? error.response.data : error.message);
            setErrorMessage('Invalid username or password');
            // Handle login failure here
        }
    };

    return (
        <div>
            <header className="bg-white shadow-md py-4">
                <div className="container mx-auto px-6 flex items-center justify-between">
                    <img src={H2PCSim} alt="Company Logo" className="h-16 w-auto" />
                    <div>
                        <Link to="/">
                            <button className="text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-md mr-2">
                                Login
                            </button>
                        </Link>
                        <Link to="/register">
                            <button className="text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-md">
                                Register
                            </button>
                        </Link>
                    </div>
                </div>
            </header>
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Login</h2>
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="rounded-md shadow-sm -space-y-px">
                            <div>
                                <label htmlFor="username" className="sr-only">Username:</label>
                                <input
                                    type="text"
                                    id="username"
                                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    value={username}
                                    onChange={handleUsernameChange}
                                    placeholder="Username"
                                />
                            </div>
                            <div>
                                <label htmlFor="password" className="sr-only">Password:</label>
                                <input
                                    type="password"
                                    id="password"
                                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    value={password}
                                    onChange={handlePasswordChange}
                                    placeholder="Password"
                                />
                            </div>
                        </div>
                        <button type="submit" className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                            Login
                        </button>
                    </form>
                    {errorMessage && <p className="mt-2 text-center text-sm text-red-600">{errorMessage}</p>}
                </div>
            </div>
        </div>
    );
};

export default Login;
