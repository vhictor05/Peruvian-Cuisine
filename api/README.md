```markdown name=api/README.md
# Peruvian Cuisine API 🍽️

API REST para el sistema integrado de Restaurant, Hotel y Discoteca.

## Información del Proyecto
- **Autor:** RCarrascoO
- **Fecha de última actualización:** 2025-06-30 02:14:32 UTC
- **Versión:** 1.0.0
- **Estado:** En desarrollo

## 📁 Estructura del Proyecto

```
api/
├── app.py              # Punto de entrada de la aplicación
├── models/            # Modelos Pydantic para validación de datos
│   ├── base.py        # Modelo base común
│   ├── restaurant.py  # Modelos del restaurante
│   ├── hotel.py      # Modelos del hotel
│   └── disco.py      # Modelos de la discoteca
├── routes/           # Rutas de la API para cada módulo
│   ├── restaurant.py
│   ├── hotel.py
│   └── disco.py
└── utils/           # Utilidades compartidas
    └── db.py        # Configuración de la base de datos
```

## 🚀 Inicio Rápido

### Requisitos Previos

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### Instalación y Ejecución

1. Clonar el repositorio:
```bash
git clone https://github.com/vhictor05/Peruvian-Cuisine.git
```

2. Navegar al directorio de la API:
```bash
cd Peruvian-Cuisine/api
```

3. Ejecutar el servidor:
```bash
python app.py
```

El servidor estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

### Acceso a la Documentación
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Endpoints Principales

#### 🍽️ Restaurant
- `GET /api/v1/restaurant/menu` - Obtener menú completo
- `POST /api/v1/restaurant/menu` - Crear nuevo ítem de menú
- `PUT /api/v1/restaurant/menu/{id}` - Actualizar ítem existente
- `DELETE /api/v1/restaurant/menu/{id}` - Eliminar ítem del menú

#### 🏨 Hotel
- `GET /api/v1/hotel/rooms` - Listar habitaciones disponibles
- `POST /api/v1/hotel/reservations` - Crear nueva reserva
- `PUT /api/v1/hotel/reservations/{id}` - Actualizar reserva
- `DELETE /api/v1/hotel/reservations/{id}` - Cancelar reserva

#### 🎵 Discoteca
- `GET /api/v1/disco/events` - Listar eventos
- `POST /api/v1/disco/tickets` - Vender entrada
- `PUT /api/v1/disco/events/{id}` - Actualizar evento
- `DELETE /api/v1/disco/events/{id}` - Cancelar evento

### Ejemplos de Uso

#### Crear ítem de menú
```http
POST http://localhost:8000/api/v1/restaurant/menu
Content-Type: application/json

{
    "name": "Lomo Saltado",
    "description": "Plato típico peruano",
    "price": 25.00,
    "category": "Platos principales",
    "available": true
}
```

#### Crear reserva de hotel
```http
POST http://localhost:8000/api/v1/hotel/reservations
Content-Type: application/json

{
    "guest_name": "Juan Pérez",
    "room_id": 101,
    "check_in": "2025-07-01",
    "check_out": "2025-07-05",
    "guests": 2
}
```

## 🔍 Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200 | Éxito - La solicitud se completó correctamente |
| 201 | Creado - El recurso se creó exitosamente |
| 204 | Sin contenido - La solicitud se completó pero no hay contenido |
| 400 | Error de solicitud - La solicitud no pudo ser procesada |
| 404 | No encontrado - El recurso solicitado no existe |
| 500 | Error del servidor - Error interno del servidor |

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
   ```bash
   git checkout -b feature/NuevaFuncionalidad
   ```
3. Commit tus cambios
   ```bash
   git commit -m 'Agregar nueva funcionalidad'
   ```
4. Push a la rama
   ```bash
   git push origin feature/NuevaFuncionalidad
   ```
5. Abre un Pull Request

## 📝 Historial de Versiones

### 1.0.0 (2025-06-30)
- Primera versión de la API
- Implementación base de endpoints REST
- Documentación inicial
- Integración con FastAPI y SQLAlchemy

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de conexión a la base de datos**
   ```
   Solución: Verificar que main.db existe en el directorio raíz
   ```

2. **Error al iniciar el servidor**
   ```
   Solución: Verificar que el puerto 8000 no esté en uso
   ```



Este README está:
1. Completamente formateado con Markdown
2. Incluye emojis para mejor legibilidad
3. Contiene todas las secciones necesarias
4. Está listo para copiar y pegar
5. Incluye ejemplos prácticos
6. Tiene una estructura clara y profesional

