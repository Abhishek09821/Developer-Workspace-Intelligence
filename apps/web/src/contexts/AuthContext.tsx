import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api } from '@/lib/api'
import type { AuthResponse, UserResponse } from '@/types/api'

interface AuthState {
  user: UserResponse | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const TOKEN_KEY = 'canary_access_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem(TOKEN_KEY),
    isLoading: true,
    isAuthenticated: false,
  })

  // On mount, verify the stored token is still valid
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setState((s) => ({ ...s, isLoading: false }))
      return
    }

    api
      .get<UserResponse>('/auth/me')
      .then((res) => {
        setState({ user: res.data, token, isLoading: false, isAuthenticated: true })
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
      })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<AuthResponse>('/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, res.data.access_token)
    setState({
      user: res.data.user,
      token: res.data.access_token,
      isLoading: false,
      isAuthenticated: true,
    })
  }, [])

  const register = useCallback(async (email: string, password: string, fullName?: string) => {
    const res = await api.post<AuthResponse>('/auth/register', {
      email,
      password,
      full_name: fullName ?? null,
    })
    localStorage.setItem(TOKEN_KEY, res.data.access_token)
    setState({
      user: res.data.user,
      token: res.data.access_token,
      isLoading: false,
      isAuthenticated: true,
    })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
  }, [])

  const value = useMemo(
    () => ({ ...state, login, register, logout }),
    [state, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
