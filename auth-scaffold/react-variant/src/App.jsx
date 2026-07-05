import { useState } from 'react';
import LoginPage          from './components/LoginPage.jsx';
import RegisterPage       from './components/RegisterPage.jsx';
import ForgotPasswordPage from './components/ForgotPasswordPage.jsx';

/** Minimal client-side router — replace with react-router-dom for production */
export default function App() {
  const [page, setPage] = useState(
    () => window.location.pathname.replace(/^\//, '') || 'login'
  );

  const navigate = (to) => {
    window.history.pushState({}, '', `/${to}`);
    setPage(to);
  };

  const props = { navigate };

  if (page === 'register')       return <RegisterPage       {...props} />;
  if (page === 'forgot-password') return <ForgotPasswordPage {...props} />;
  return <LoginPage {...props} />;
}
