export default function DarkModeToggle({ darkMode, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="fixed bottom-5 right-5 w-11 h-11 rounded-full flex items-center justify-center
                 text-xl z-50 backdrop-blur-md border border-white/30 bg-white/20
                 hover:bg-white/30 transition-colors focus-visible:outline
                 focus-visible:outline-3 focus-visible:outline-white focus-visible:outline-offset-2"
      aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-pressed={darkMode}
    >
      {darkMode ? '☀️' : '🌙'}
    </button>
  );
}
