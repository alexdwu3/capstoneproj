# Capstone Project - Casting Agency API

## 🚀 Project Overview

The Casting Agency API is a backend service for managing movies and actors. It allows users to view, create, update, and delete movies and actors based on their assigned roles and permissions. The API is secured using Auth0 and follows Role-Based Access Control (RBAC) to restrict actions based on user roles.

## 🌍 Hosted API URL

The API is live and accessible at:
🔗 [https://udacity-capstone-10101.herokuapp.com]

## 📌 Authentication & Authorization

This project uses Auth0 for authentication. Users must provide a valid JWT token with the necessary permissions to access the API.

## 🔑 Roles & Permissions

The application defines the following roles:

### Casting Assistant 🎬
- Can view actors and movies (GET requests only)

### Casting Director 🎭
- Can view actors and movies
- Can add or delete actors
- Can modify actors and movies

### Executive Producer 🎬🎥
- Has full access, including creating and deleting movies

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/alexdwu3/capstoneproj
cd capstone-project

The API will be available at http://127.0.0.1:8080.

🔥 API Endpoints
Movies 🎥
Method	Endpoint	Description	Permission
GET	/movies	Get all movies	All roles
POST	/movies	Add a new movie	Executive Producer
PATCH	/movies/<id>	Update a movie	Casting Director & Executive Producer
DELETE	/movies/<id>	Delete a movie	Executive Producer
Actors 🎭
Method	Endpoint	Description	Permission
GET	/actors	Get all actors	All roles
POST	/actors	Add a new actor	Casting Director & Executive Producer
PATCH	/actors/<id>	Update an actor	Casting Director & Executive Producer
DELETE	/actors/<id>	Delete an actor	Casting Director & Executive Producer

✅ Running Tests
The test suite includes unit tests for all API endpoints and RBAC behavior.

-- python test_app.py

🎯 Final Checklist Before Submission
✅ All API endpoints work in Postman
✅ Auth0 roles & permissions correctly configured
✅ Tests pass successfully
✅ README is complete & well-documented
✅ Heroku app is live and accessible
📜 Auth0 Environment Variables


🔑 JWT Token for Testing
Here is a token so that you can test the APIs locally. The token is valid for 7 days and has all the permissions:
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRIcXpvVGVhTFBmVkZPaTlobkIyQiJ9.eyJpc3MiOiJodHRwczovL2Rldi1lemY1Z3BkZzR1czAzMWhhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiI1ZFVWbGVXQjROc0hyRElyYk1iSzZCWkNPakRQb3RhVUBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9jYXN0aW5nLWFnZW5jeS1hcGkiLCJpYXQiOjE3NDAyMDM0ODAsImV4cCI6MTc0MDgwODI3Nywic2NvcGUiOiJnZXQ6YWN0b3JzIGdldDptb3ZpZXMgcG9zdDphY3RvcnMgcG9zdDptb3ZpZXMgcGF0Y2g6YWN0b3JzICBwYXRjaDptb3ZpZXMgZGVsZXRlOmFjdG9ycyBkZWxldGU6bW92aWVzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwiYXpwIjoiNWRVVmxlV0I0TnNIckRJcmJNYks2QlpDT2pEUG90YVUiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiLCJwYXRjaDphY3RvcnMgIiwicGF0Y2g6bW92aWVzIiwiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiXX0.xvbtOePCEGwX8ycsoMvK5CoI43xx962AE0JuIFGAGW3V2qLvQWJD415funH1eClTXE89w-Wb1tk-jh9pLKonQY4XO9UiC87H2CKMcjfv7rmC98lZ1LRT0Q3HNhgAFNJDt64khvkAeymj_cm7qQzTCo_2Ygx5PTKcT1T3kUNCjnPCxQsx9CTeuDWgeWgA53kupFq0lmrHeK6BDssggzBBlpGF1_Hg5zTEHAfNTsADkVCNrldwyKP7NaFh1nbcDOXr4J8_UVa_VYLyTsfDl68q0cXg_GZjnpy6B-ZijriFCf4sUD2unt1q6YPL8TcMDuYa15WebNH0MTi5NCjUgOgl5g


If you want to generate a token yourself use the following body as a POST to https://dev-ezf5gpdg4us031ha.us.auth0.com/oauth/token
{
    "client_id": "5dUVleWB4NsHrDIrbMbK6BZCOjDPotaU",
    "client_secret": "oc1drrrrshY20AOPMlOP3HnszCnSWQjsSqXZEH5sEIF5EsIE6jgOC066pu-Q1gx7",
    "audience": "https://casting-agency-api",
    "grant_type": "client_credentials"
}



sample get movies endpoint to heroku app:
GET https://udacity-capstone-10101-1be8438ef288.herokuapp.com/movies

with bearer token