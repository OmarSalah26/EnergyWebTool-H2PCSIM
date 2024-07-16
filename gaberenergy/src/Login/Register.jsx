import React, { useState } from 'react';
import axios from 'axios';
import H2PCSim from '/H2PCSS.png'; // Adjust the path as needed
import { Link } from 'react-router-dom';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');

    const handleRegister = (e) => {
        e.preventDefault();
        axios.post('http://localhost:5000/api/register', { username, password, role })
            .then(response => {
                console.log('Response from server:', response.data);
            })
            .catch(error => {
                console.error('Error sending data to server:', error);
            });
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
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Register</h2>
                    <form className="mt-8 space-y-6" onSubmit={handleRegister}>
                        <div className="rounded-md shadow-sm -space-y-px">
                            <div>
                                <label htmlFor="username" className="sr-only">Username</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    placeholder="Username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div>
                                <label htmlFor="password" className="sr-only">Password</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            <div>
                                <label htmlFor="role" className="sr-only">Role</label>
                                <select
                                    id="role"
                                    name="role"
                                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    value={role}
                                    onChange={(e) => setRole(e.target.value)}
                                >
                                    <option value="">Select Role</option>
                                    <option value="admin">Admin</option>
                                    <option value="user">User</option>
                                    <option value="manager">Manager</option>
                                </select>
                            </div>
                        </div>
                        <button
                            type="submit"
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Register
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Register;
