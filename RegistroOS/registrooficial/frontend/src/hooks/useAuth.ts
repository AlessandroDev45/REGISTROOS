import { useState, useEffect } from 'react';
import api from '../services/api';

interface User {
  id: number;
  email: string;
  nome_completo: string;
  privilege_level: string;
  setor: string;
  departamento: string;
}

const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await api.get('/me');
        setUser(response.data);
      } catch (error) {
        // Token is invalid or user not authenticated
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  return { user, loading };
};

export default useAuth;
