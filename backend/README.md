# Presence_App
# School Attendance Management System - BACKEND

Une application FastAPI pour gérer les présences des élèves dans une école.

## 🚀 Fonctionnalités

- Enregistrement en tant user
- Connection avec identifiant

## 🛠️ Installation

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour le développement)

### Démarrage rapide

```bash
# Cloner le projet
git clone <votre-repo>
cd vde_attendance

# Démarrer avec Docker
docker-compose up -d --build

# L'application sera disponible sur:
# API: http://attendance.localhost
# Traefik Dashboard: http://localhost:8080

# ✅Alternative hors Docker :
# Placez-vous dans le dossier backend :
cd vde_attendance/backend

# Puis lancez le serveur FastAPI avec Uvicorn :
python -m uvicorn app.main:app --reload

```
# API Reference
> Base URL: `http://127.0.0.1:8000`

## Accédez à la documentation Swagger :
> Docs URL: `http://127.0.0.1:8000/docs`
## Authentication



### Register User
```http
POST /api/auth/register
```
| Parameter  | Type     | Description              |
| :--------- | :------- | :----------------------- |
| `email`    | `string` | **Required**. User email |
| `password` | `string` | **Required**. Password   |

### Login User
```http
POST /api/auth/login
```
| Parameter  | Type     | Description              |
| :--------- | :------- | :----------------------- |
| `email`    | `string` | **Required**. User email |
| `password` | `string` | **Required**. Password   |

### Login Pour l'Access Token
```http
POST /api/auth/token
```
| Parameter  | Type     | Description                     |
| :--------- | :------- | :------------------------------ |
| `username` | `string` | **Required**. Username or email |
| `password` | `string` | **Required**. Password          |

### Read Current User
```http
GET /api/auth/me
```
| Header          | Type     | Description                       |
| :-------------- | :------- | :-------------------------------- |
| `Authorization` | `string` | **Required**. Bearer access token |


### List Users
```http
GET /api/auth/users
```
GET /api/auth/users


### Déactiver User
```http
PUT /api/auth/users/{user_id}/deactivate
```
| Parameter | Type     | Description                  |
| :-------- | :------- | :--------------------------- |
| `user_id` | `string` | **Required**. ID of the user |
| Header    | `string` | **Required**. Bearer token   |


### Lister tous les Items
```http
GET /api/items
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

### Aficher un Item via son ID
```http
GET /api/items/${id}
```
| Parameter | Type     | Description                  |
| :-------- | :------- | :--------------------------- |
| `id`      | `string` | **Required**. ID of the item |
