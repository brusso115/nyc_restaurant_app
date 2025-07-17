import { useEffect, useRef } from 'react'
import '../styles/CategoryDropdown.css'

function CategoryDropdown({ categories, selected, onChange, open, setOpen }) {
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [setOpen])

  return (
    <div className="dropdown-container" ref={dropdownRef}>
      <button className="dropdown-toggle" onClick={() => setOpen(!open)}>
        Filter by Categories ▾
      </button>

      {open && (
        <div className="dropdown-menu">
          <div className="dropdown-controls">
            <button className="dropdown-button" onClick={() => onChange(categories)}>Select All</button>
            <button className="dropdown-button" onClick={() => onChange([])}>Clear All</button>
          </div>

          {categories.map((cat, i) => (
            <label key={i} className="dropdown-option">
              <input
                type="checkbox"
                value={cat}
                checked={selected.includes(cat)}
                onChange={() => {
                  const next = selected.includes(cat)
                    ? selected.filter(c => c !== cat)
                    : [...selected, cat]
                  onChange(next)
                }}
                className="dropdown-checkbox"
              />
              {cat}
            </label>
          ))}
        </div>
      )}
    </div>
  )
}

export default CategoryDropdown