import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
    const token = localStorage.getItem('access_token');

    if (!token) {
        // 未登录，重定向到登录页
        return <Navigate to="/login" replace />;
    }

    return children;
}

export default ProtectedRoute;
