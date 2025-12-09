import { useState, useCallback } from 'react'

let toastId = 0

export const useToast = () => {
  const [toasts, setToasts] = useState([])

  const showToast = useCallback((message, type = 'success', duration = 3000) => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, message, type, duration }])
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const showSuccess = useCallback((message, duration) => {
    return showToast(message, 'success', duration)
  }, [showToast])

  const showError = useCallback((message, duration) => {
    return showToast(message, 'error', duration)
  }, [showToast])

  const showInfo = useCallback((message, duration) => {
    return showToast(message, 'info', duration)
  }, [showToast])

  const showWarning = useCallback((message, duration) => {
    return showToast(message, 'warning', duration)
  }, [showToast])

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    removeToast,
  }
}





