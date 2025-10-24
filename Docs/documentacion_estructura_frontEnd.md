# SKYNET - DOCUMENTACIÓN DE ESTRUCTURA FRONTEND

## Sistema de Gestión de Visitas Técnicas

### TABLA DE CONTENIDOS

1. [Arquitectura General](#arquitectura-general)
2. [Módulo de Usuarios](#módulo-de-usuarios)
3. [Módulo de Clientes](#módulo-de-clientes)
4. [Módulo de Visitas](#módulo-de-visitas)
5. [Módulo de Configuraciones](#módulo-de-configuraciones)
6. [Interfaces y DTOs](#interfaces-y-dtos)
7. [Servicios y API Endpoints](#servicios-y-api-endpoints)
8. [Flujos de Datos](#flujos-de-datos)

---

## ARQUITECTURA GENERAL

### Estructura de Carpetas

```
src/app/
├── core/
│   ├── guards/
│   │   └── auth.guard.ts
│   ├── interfaces/
│   │   ├── index.ts
│   │   ├── usuario.ts
│   │   ├── cliente.ts
│   │   ├── visita.ts
│   │   └── configuracion.ts
│   └── services/
│       ├── auth.service.ts
│       ├── base-api.service.ts
│       ├── mock-data.service.ts
│       ├── usuario.service.ts
│       ├── cliente.service.ts
│       ├── visita.service.ts
│       └── configuracion.service.ts
├── features/
│   ├── admin/
│   ├── public/
│   ├── usuarios/
│   ├── clientes/
│   ├── visitas/
│   └── configuraciones/
└── shared/
    ├── services/
    └── components/
```

### Tecnologías Frontend

- **Framework**: Angular 19.1.0
- **UI Framework**: Bootstrap 5.3.8
- **Componentes**: Standalone Components
- **Routing**: Lazy Loading por módulos
- **Estado**: Servicios con RxJS Observables
- **Validaciones**: Reactive Forms

---

## MÓDULO DE USUARIOS

### Entidades y Relaciones

```typescript
interface Usuario {
  idUsuario: number;
  nombre: string;
  apellido: string;
  email: string;
  telefono?: string;
  rol: RoleTipo;
  activo: boolean;
  fechaCreacion: Date;
  fechaActualizacion: Date;
}

enum RoleTipo {
  ADMINISTRADOR = "ADMINISTRADOR",
  SUPERVISOR = "SUPERVISOR",
  TECNICO = "TECNICO",
}
```

### Funcionalidades

- **CRUD Completo**: Crear, leer, actualizar, eliminar usuarios
- **Gestión de Roles**: Administrador, Supervisor, Técnico
- **Filtros**: Por rol, estado (activo/inactivo), búsqueda por texto
- **Validaciones**: Email único, teléfono guatemalteco, contraseñas seguras

### Endpoints Esperados

```
GET    /api/usuarios/                    # Lista paginada con filtros
GET    /api/usuarios/{id}/               # Detalle de usuario
POST   /api/usuarios/                    # Crear usuario
PUT    /api/usuarios/{id}/               # Actualizar usuario
DELETE /api/usuarios/{id}/               # Eliminar usuario
POST   /api/usuarios/{id}/toggle-status/ # Activar/Desactivar
```

---

## MÓDULO DE CLIENTES

### Entidades y Relaciones

```typescript
interface Cliente {
  idCliente: number;
  nombre: string;
  contacto: string;
  telefono: string;
  email: string;
  direccion: string;
  latitud?: number;
  longitud?: number;
  tipoCliente: TipoCliente;
  activo: boolean;
  fechaCreacion: Date;
  fechaActualizacion: Date;
  // Relaciones
  visitas?: Visita[];
}

enum TipoCliente {
  CORPORATIVO = "CORPORATIVO",
  INDIVIDUAL = "INDIVIDUAL",
  GOBIERNO = "GOBIERNO",
}
```

### Funcionalidades

- **CRUD Completo**: Gestión integral de clientes
- **Geolocalización**: Integración con Google Maps para coordenadas
- **Tipos de Cliente**: Corporativo, Individual, Gobierno
- **Filtros**: Por tipo, estado, búsqueda por texto
- **Validaciones**: Email, teléfono, dirección requerida

### Endpoints Esperados

```
GET    /api/clientes/                    # Lista paginada con filtros
GET    /api/clientes/{id}/               # Detalle de cliente
POST   /api/clientes/                    # Crear cliente
PUT    /api/clientes/{id}/               # Actualizar cliente
DELETE /api/clientes/{id}/               # Eliminar cliente
GET    /api/clientes/{id}/visitas/       # Visitas del cliente
```

---

## MÓDULO DE VISITAS

### Entidades y Relaciones

```typescript
interface Visita {
  idVisita: number;
  clienteId: number;
  tecnicoId: number;
  supervisorId?: number;
  fechaProgramada: Date;
  fechaInicio?: Date;
  fechaFin?: Date;
  estado: EstadoVisita;
  tipoVisita: TipoVisita;
  descripcion: string;
  observaciones?: string;
  latitud?: number;
  longitud?: number;
  fechaCreacion: Date;
  fechaActualizacion: Date;
  // Relaciones
  cliente?: Cliente;
  tecnico?: Usuario;
  supervisor?: Usuario;
  ejecuciones?: Ejecucion[];
}

enum EstadoVisita {
  PROGRAMADA = "PROGRAMADA",
  EN_PROGRESO = "EN_PROGRESO",
  COMPLETADA = "COMPLETADA",
  CANCELADA = "CANCELADA",
  REPROGRAMADA = "REPROGRAMADA",
}

enum TipoVisita {
  MANTENIMIENTO = "MANTENIMIENTO",
  INSTALACION = "INSTALACION",
  REPARACION = "REPARACION",
  INSPECCION = "INSPECCION",
}

interface Ejecucion {
  idEjecucion: number;
  visitaId: number;
  descripcion: string;
  tiempoInicio: Date;
  tiempoFin?: Date;
  completada: boolean;
  observaciones?: string;
  evidenciaFoto?: string;
  fechaCreacion: Date;
}
```

### Funcionalidades

- **CRUD Completo**: Gestión de visitas técnicas
- **Estados de Workflow**: Programada → En Progreso → Completada/Cancelada
- **Asignación de Técnicos**: Por supervisor o administrador
- **Geolocalización**: Tracking GPS de visitas
- **Ejecuciones**: Subtareas dentro de cada visita
- **Filtros**: Por estado, técnico, cliente, fecha

### Endpoints Esperados

```
GET    /api/visitas/                     # Lista paginada con filtros
GET    /api/visitas/{id}/                # Detalle de visita
POST   /api/visitas/                     # Crear visita
PUT    /api/visitas/{id}/                # Actualizar visita
DELETE /api/visitas/{id}/                # Eliminar visita
POST   /api/visitas/{id}/iniciar/        # Iniciar visita
POST   /api/visitas/{id}/completar/      # Completar visita
POST   /api/visitas/{id}/cancelar/       # Cancelar visita
GET    /api/visitas/{id}/ejecuciones/    # Ejecuciones de la visita
POST   /api/visitas/{id}/ejecuciones/    # Crear ejecución
PUT    /api/ejecuciones/{id}/            # Actualizar ejecución
```

---

## MÓDULO DE CONFIGURACIONES

### Entidades y Relaciones

```typescript
interface Configuracion {
  id: number;
  clave: string;
  valor: string;
  categoria: CategoriaConfiguracion;
  descripcion?: string;
  tipo: TipoConfiguracion;
  valorPorDefecto: string;
  esPublica: boolean;
  esEditable: boolean;
  fechaCreacion: Date;
  fechaActualizacion: Date;
  creadoPor: number;
  modificadoPor?: number;
}

enum CategoriaConfiguracion {
  GENERAL = "GENERAL",
  EMAIL = "EMAIL",
  MAPAS = "MAPAS",
  RESPALDOS = "RESPALDOS",
  SEGURIDAD = "SEGURIDAD",
  NOTIFICACIONES = "NOTIFICACIONES",
}

enum TipoConfiguracion {
  TEXTO = "TEXTO",
  NUMERO = "NUMERO",
  BOOLEAN = "BOOLEAN",
  EMAIL = "EMAIL",
  URL = "URL",
  PASSWORD = "PASSWORD",
  JSON = "JSON",
}

interface LogAuditoria {
  id: number;
  entidad: string;
  idEntidad: number;
  accion: AccionAuditoria;
  valorAnterior?: string;
  valorNuevo?: string;
  descripcion: string;
  direccionIP: string;
  userAgent: string;
  fechaCreacion: Date;
  creadoPor: number;
}

enum AccionAuditoria {
  CREAR = "CREAR",
  ACTUALIZAR = "ACTUALIZAR",
  ELIMINAR = "ELIMINAR",
  LOGIN = "LOGIN",
  LOGOUT = "LOGOUT",
  CAMBIO_PASSWORD = "CAMBIO_PASSWORD",
  ACCESO_DENEGADO = "ACCESO_DENEGADO",
}

interface RespaldoSistema {
  id: number;
  tipo: TipoRespaldo;
  descripcion?: string;
  rutaArchivo: string;
  tamanoBytes: number;
  archivos?: string[];
  estado: EstadoRespaldo;
  version?: string;
  fechaCreacion: Date;
  fechaFinalizacion?: Date;
  duracionSegundos?: number;
  creadoPor: number;
  comprimido: boolean;
  errorMensaje?: string;
}

enum TipoRespaldo {
  COMPLETO = "COMPLETO",
  INCREMENTAL = "INCREMENTAL",
  CONFIGURACIONES = "CONFIGURACIONES",
  USUARIOS = "USUARIOS",
  CLIENTES = "CLIENTES",
}

enum EstadoRespaldo {
  EN_PROGRESO = "EN_PROGRESO",
  COMPLETADO = "COMPLETADO",
  FALLIDO = "FALLIDO",
  CANCELADO = "CANCELADO",
}
```

### Funcionalidades

- **Gestión de Configuraciones**: Por categorías (General, Email, Mapas, etc.)
- **Logs de Auditoría**: Registro de todas las acciones del sistema
- **Sistema de Respaldos**: Creación, descarga y restauración
- **Validaciones**: Específicas por tipo de configuración
- **Filtros**: Por categoría, fecha, usuario, acción

### Endpoints Esperados

```
GET    /api/configuraciones/             # Lista con filtros por categoría
GET    /api/configuraciones/{id}/        # Detalle de configuración
POST   /api/configuraciones/             # Crear configuración
PUT    /api/configuraciones/{id}/        # Actualizar configuración
DELETE /api/configuraciones/{id}/        # Eliminar configuración
GET    /api/configuraciones/categoria/{cat}/ # Por categoría

GET    /api/logs-auditoria/              # Lista con filtros
POST   /api/logs-auditoria/              # Crear log (automático)

GET    /api/respaldos/                   # Lista de respaldos
POST   /api/respaldos/                   # Crear respaldo
DELETE /api/respaldos/{id}/              # Eliminar respaldo
GET    /api/respaldos/{id}/descargar/    # Descargar respaldo
POST   /api/respaldos/{id}/restaurar/    # Restaurar respaldo
```

---

## SERVICIOS Y PATRÓN DE COMUNICACIÓN

### Base API Service

```typescript
class BaseApiService {
  protected apiUrl = environment.apiUrl;

  protected handleError(error: any): Observable<never>;
  protected getHttpOptions(): { headers: HttpHeaders };
}
```

### Patrón de Servicios

Todos los servicios extienden BaseApiService y siguen este patrón:

```typescript
class ExampleService extends BaseApiService {
  getAll(filters?: FilterDTO): Observable<Entity[]>;
  getById(id: number): Observable<Entity>;
  create(entity: CreateDTO): Observable<Entity>;
  update(id: number, entity: UpdateDTO): Observable<Entity>;
  delete(id: number): Observable<void>;
}
```

---

## FLUJOS DE DATOS CRÍTICOS

### 1. Flujo de Autenticación

```
Login → AuthService → JWT Token → Local Storage → HTTP Interceptor
```

### 2. Flujo de Visitas

```
Crear Visita → Asignar Técnico → Programar → Ejecutar → Completar
Estados: PROGRAMADA → EN_PROGRESO → COMPLETADA
```

### 3. Flujo de Auditoría

```
Cualquier Acción CRUD → Automático Log → Base de Datos
Captura: Usuario, IP, UserAgent, Valores Anterior/Nuevo
```

### 4. Flujo de Respaldos

```
Trigger Manual/Automático → Crear Respaldo → Comprimir → Almacenar → Notificar
```

---

## VALIDACIONES Y REGLAS DE NEGOCIO

### Usuarios

- Email único en el sistema
- Teléfono formato guatemalteco (+502)
- Solo administradores pueden crear usuarios
- Supervisores pueden gestionar técnicos

### Clientes

- Email único por cliente
- Dirección requerida para geolocalización
- Validación de coordenadas GPS

### Visitas

- No pueden programarse en fechas pasadas
- Técnico no puede tener visitas simultáneas
- Solo el técnico asignado puede iniciar/completar
- Supervisores pueden reasignar visitas

### Configuraciones

- Solo administradores pueden modificar
- Validaciones específicas por tipo
- Logs automáticos en cada cambio
- Respaldos programables

---

## ESTRUCTURA DE RESPUESTAS API

### Respuesta Estándar

```typescript
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
}
```

### Respuesta Paginada

```typescript
interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
  };
  message?: string;
}
```

### Códigos de Estado HTTP

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado
- **400**: Bad Request - Datos inválidos
- **401**: Unauthorized - Sin autenticación
- **403**: Forbidden - Sin permisos
- **404**: Not Found - Recurso no encontrado
- **500**: Internal Server Error - Error del servidor

---

## CONFIGURACIÓN DE ENTORNO

### Variables de Entorno Frontend

```typescript
export const environment = {
  production: false,
  apiUrl: "http://localhost:8000/api/",
  googleMapsApiKey: "YOUR_GOOGLE_MAPS_KEY",
  appVersion: "1.0.0",
};
```

### Headers HTTP Esperados

```
Authorization: Bearer {jwt_token}
Content-Type: application/json
Accept: application/json
X-CSRFToken: {csrf_token} (para Django)
```
