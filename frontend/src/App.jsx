import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import MainApp from './components/MainApp';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={<Login />} />

        {/* 主应用（受保护） */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <MainApp />
            </ProtectedRoute>
          }
        />

        {/* 默认重定向 */}
        <Route
          path="/"
          element={
            localStorage.getItem('access_token')
              ? <Navigate to="/app" replace />
              : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
