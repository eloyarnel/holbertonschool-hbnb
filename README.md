# 🏨 HBnB Evolution

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Layered-blue?style=for-the-badge" alt="Architecture">
  <img src="https://img.shields.io/badge/Design%20Pattern-Facade%20%26%20Repository-green?style=for-the-badge" alt="Patterns">
  <img src="https://img.shields.io/badge/OOP-SOLID-red?style=for-the-badge" alt="OOP">
</p>

## 📝 Overview

**HBnB Evolution** is a lightweight, simplified property rental platform inspired by modern services like Airbnb. The application empowers users to register accounts, list properties, write comprehensive reviews, and manage property amenities seamlessly.

The core mission of this project is to design and implement a highly scalable, maintainable web application architecture by strict application of **Object-Oriented Programming (OOP)** principles and robust **Software Design Patterns**.

---

## 🎯 Project Objectives

*   **Modular Architecture:** Design a system with clean separation of concerns for long-term maintainability.
*   **Domain-Driven Entities:** Implement robust core entities (`User`, `Place`, `Review`, `Amenity`) representing real-world business logic.
*   **SOLID Principles:** Apply strict object-oriented programming standards.
*   **Layered Design:** Decouple components completely across presentation, business, and storage tiers.
*   **Visual Documentation:** Map out and detail every system interaction using comprehensive UML modeling.

---

## 🏗️ System Architecture

The application is structured following a strict **3-Layer Architecture**, ensuring that each component has one focused responsibility.


┌─────────────────────────────────────────┐
│           Presentation Layer            │  <-- Handles HTTP Requests / API
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│          Business Logic Layer           │  <-- Core Domain Models & Rules
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│            Persistence Layer            │  <-- Database Access / Repositories
└─────────────────────────────────────────┘

### 🎛️ 1. Presentation Layer (API & Services)
Acts as the frontline communicator between external clients and the application core.
*   Receives and parses incoming client HTTP requests.
*   Enforces input data sanitization and syntactical validation.
*   Formats and returns structured API responses.

### 🧠 2. Business Logic Layer (Models)
The central brain of HBnB. This layer houses the core business entities and orchestrates operational rules.
*   Manages domain states, behaviors, and lifecycle rules.
*   Processes application-specific workflows and calculations.
*   Coordinates relationships and interactions between core objects.

### 💾 3. Persistence Layer (Database Abstraction)
The data custodian. It abstracts all low-level storage logic away from the business rules.
*   Handles secure data serialization and hard writes.
*   Optimizes data retrieval and query execution.
*   Manages direct database connections and repository abstractions.

---

## 💎 Core Entities & Schema

Every model in the system extends from a unified `BaseModel` that injects a unique identifier (`UUID4`) and audit timestamps (`created_at`, `updated_at`).

### 👤 User
Represents any registered member of the platform (Hosts, Guests, and Admins).
```python
# Key Attributes
- first_name:  string
- last_name:   string
- email:       string  # Unique identifier
- password:    string  # Hashed
- is_admin:    boolean

## Author
Eloy A. Alicea Sanchez

