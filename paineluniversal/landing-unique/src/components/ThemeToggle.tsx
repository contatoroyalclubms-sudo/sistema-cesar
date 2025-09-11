import React from 'react'
import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const getIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun className="h-4 w-4" />
      case 'dark':
        return <Moon className="h-4 w-4" />
      case 'system':
        return <Monitor className="h-4 w-4" />
      default:
        return <Sun className="h-4 w-4" />
    }
  }

  const getTitle = () => {
    switch (theme) {
      case 'light':
        return 'Modo Claro'
      case 'dark':
        return 'Modo Escuro'
      case 'system':
        return 'Sistema'
      default:
        return 'Modo Claro'
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleTheme}
      title={getTitle()}
      className={cn(
        "relative h-9 w-9 px-0 transition-all duration-300 hover:bg-primary/10",
        "border border-transparent hover:border-primary/20"
      )}
    >
      <div className="transition-all duration-300 hover:scale-110">
        {getIcon()}
      </div>
      <span className="sr-only">{getTitle()}</span>
    </Button>
  )
}