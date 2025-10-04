import React from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './ui/App'
import './ui/theme.css'

createRoot(document.getElementById('root')!).render(<App />)
