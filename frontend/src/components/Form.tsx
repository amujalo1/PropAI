/**
 * Reusable Form component
 */
interface FormProps {
  onSubmit: (data: any) => void
  children: React.ReactNode
}

export function Form({ onSubmit, children }: FormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget as HTMLFormElement)
    const data = Object.fromEntries(formData)
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {children}
    </form>
  )
}
