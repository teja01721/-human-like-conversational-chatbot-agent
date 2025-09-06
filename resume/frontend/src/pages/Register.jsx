import React, { useState, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const validateForm = () => {
    // Check if passwords match
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return false;
    }
    
    // Check password length
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    
    // Check username format
    if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
      setError('Username must be alphanumeric');
      return false;
    }
    
    // Check email format
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  const { register } = useContext(AuthContext);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await register({
        email: formData.email,
        username: formData.username,
        full_name: formData.full_name,
        password: formData.password
      });
      
      if (result.success) {
        // Registration successful, redirect to login
        navigate('/login');
      } else {
        setError(result.error || 'Failed to register. Please try again.');
      }
    } catch (err) {
      // Handle unexpected errors
      setError('An unexpected error occurred. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '500px', margin: '2rem auto' }}>
        <div className="card-header text-center">
          <h2>Create Account</h2>
          <p className="text-muted">Join our community today</p>
        </div>
        
        <div className="card-body">
        
          {error && (
            <div className="alert alert-error mb-4" role="alert">
              <div className="d-flex align-items-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" className="me-2">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                  <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
                </svg>
                <span>{error}</span>
              </div>
            </div>
          )
        
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">
                Email Address *
              </label>
              <input
                className="form-control"
                id="email"
                type="email"
                name="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="username">
                Username *
              </label>
              <input
                className="form-control"
                id="username"
                type="text"
                name="username"
                placeholder="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="full_name">
                Full Name
              </label>
              <input
                className="form-control"
                id="full_name"
                type="text"
                name="full_name"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={handleChange}
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="password">
                Password *
              </label>
              <input
                className="form-control"
                id="password"
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <small className="form-text text-muted">Must be at least 8 characters long</small>
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="confirm_password">
                Confirm Password *
              </label>
              <input
                className="form-control"
                id="confirm_password"
                type="password"
                name="confirm_password"
                placeholder="••••••••"
                value={formData.confirm_password}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group mt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-100"
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Creating Account...
                  </>
                ) : (
                  'Create Account'
                )}
              </button>
            </div>
          </form>
        </div>
        
        <div className="card-footer text-center">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="text-primary">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;