"""
Color Studio — Theme Manager
Singleton gérant le basculement thème sombre / thème clair.
"""

from PyQt6.QtCore import QObject, pyqtSignal

THEMES = {
    'dark': {
        # Arrière-plans
        'bg_primary':         '#2b2b2b',
        'bg_secondary':       '#222222',
        'bg_card':            '#303030',
        'bg_input':           '#222222',
        'bg_render':          '#1e1e1e',
        'bg_section_content': '#2e2e2e',
        'bg_side':            '#272727',
        # Bordures
        'border_subtle':      '#1a1a1a',
        'border_mid':         '#333333',
        'border_strong':      '#444444',
        'border_input':       '#1e1e1e',
        # Textes
        'text_primary':       '#cccccc',
        'text_secondary':     '#aaaaaa',
        'text_muted':         '#777777',
        'text_dim':           '#555555',
        # Label valeur d'exposition
        'exp_bg':             '#222222',
        'exp_color':          '#aaaaaa',
        'exp_border':         '#1e1e1e',
        # Label AE (teinte bleue spécifique)
        'ae_bg':              '#0f0f22',
        'ae_color':           '#7cd4f7',
        'ae_border':          '#2a4a6a',
        # Popup roue chromatique
        'wheel_bg':           '#2a2a2a',
        'wheel_border':       '#444444',
        'wheel_close_bg':     'rgba(30,30,30,0.85)',
        'wheel_close_color':  '#777777',
        'wheel_close_border': '#444444',
        # Séparateur dans le panneau de contrôle lumière
        'divider':            '#2a2a4a',
        # Bouton toggle AE actif / inactif
        'ae_btn_on_bg':       '#333333',
        'ae_btn_on_color':    '#aaaaaa',
        'ae_btn_on_border':   '#1e1e1e',
        'ae_btn_off_bg':      '#2a2a2a',
        'ae_btn_off_color':   '#777777',
        'ae_btn_off_border':  '#1a1a1a',
    },
    'light': {
        # Arrière-plans
        'bg_primary':         '#f2f2f2',
        'bg_secondary':       '#e6e6e6',
        'bg_card':            '#ebebeb',
        'bg_input':           '#ffffff',
        'bg_render':          '#d4d4d4',
        'bg_section_content': '#eeeeee',
        'bg_side':            '#e8e8e8',
        # Bordures
        'border_subtle':      '#cccccc',
        'border_mid':         '#c4c4c4',
        'border_strong':      '#b8b8b8',
        'border_input':       '#c0c0c0',
        # Textes
        'text_primary':       '#1e1e1e',
        'text_secondary':     '#444444',
        'text_muted':         '#666666',
        'text_dim':           '#888888',
        # Label valeur d'exposition
        'exp_bg':             '#ffffff',
        'exp_color':          '#333333',
        'exp_border':         '#c0c0c0',
        # Label AE (teinte bleue claire)
        'ae_bg':              '#e8f0fe',
        'ae_color':           '#1a5a9a',
        'ae_border':          '#90b8d8',
        # Popup roue chromatique
        'wheel_bg':           '#f5f5f5',
        'wheel_border':       '#bbbbbb',
        'wheel_close_bg':     'rgba(230,230,230,0.95)',
        'wheel_close_color':  '#888888',
        'wheel_close_border': '#bbbbbb',
        # Séparateur dans le panneau de contrôle lumière
        'divider':            '#c8c8d8',
        # Bouton toggle AE actif / inactif
        'ae_btn_on_bg':       '#e0e0e0',
        'ae_btn_on_color':    '#333333',
        'ae_btn_on_border':   '#c0c0c0',
        'ae_btn_off_bg':      '#ebebeb',
        'ae_btn_off_color':   '#999999',
        'ae_btn_off_border':  '#d0d0d0',
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────────────────────────────────────
class ThemeManager(QObject):
    """Singleton gérant le thème courant et diffusant les changements."""

    theme_changed = pyqtSignal(str)   # émet 'dark' ou 'light'

    _instance: 'ThemeManager | None' = None

    @classmethod
    def instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._theme = 'dark'

    @property
    def name(self) -> str:
        """Retourne le nom du thème courant : 'dark' ou 'light'."""
        return self._theme

    def is_dark(self) -> bool:
        return self._theme == 'dark'

    def colors(self) -> dict:
        """Retourne le dictionnaire de couleurs du thème courant."""
        return THEMES[self._theme]

    def set_theme(self, name: str):
        """Bascule vers un thème nommé et émet theme_changed si changement."""
        if name in THEMES and name != self._theme:
            self._theme = name
            self.theme_changed.emit(name)

    def toggle(self):
        """Bascule entre sombre et clair."""
        self.set_theme('light' if self._theme == 'dark' else 'dark')