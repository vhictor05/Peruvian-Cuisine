# Este archivo se encarga de iniciar la aplicacion de reportes

from apps.Reportes.interfaz import ReportesApp

if __name__ == "__main__":
    app = ReportesApp()
    app.mainloop()