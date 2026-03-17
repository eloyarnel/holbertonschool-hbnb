HBnB Evolution
Overview

HBnB Evolution is a simplified property rental platform inspired by services like Airbnb. The application allows users to register accounts, list properties, write reviews for places, and associate amenities with properties.

The goal of this project is to design and implement the architecture of a scalable web application while applying object-oriented programming principles and software design patterns.

Project Objectives

The main objectives of this project are:

Design a modular and maintainable system architecture

Implement core entities such as users, places, reviews, and amenities

Apply object-oriented programming principles

Implement a layered architecture separating concerns between components

Document system design using UML diagrams

System Architecture

The application follows a layered architecture composed of three main layers:

Presentation Layer

The presentation layer handles communication between the client and the application. It receives requests and returns responses through API endpoints.

Responsibilities include:

Handling client requests

Validating input data

Returning responses

Business Logic Layer

The business logic layer contains the core models and services responsible for implementing the application's rules.

Responsibilities include:

Managing domain entities

Processing application logic

Coordinating interactions between objects

Persistence Layer

The persistence layer manages data storage and retrieval from the database.

Responsibilities include:

Saving data

Retrieving stored data

Managing database access

Core Entities

The system is built around several core entities.

User

Represents a user of the platform.

Attributes include:

first_name

last_name

email

password

Users can create places and write reviews.

Place

Represents a property listed on the platform.

Attributes include:

title

description

price

owner

address

max_guests

Each place belongs to a user and can receive reviews.

Review

Represents feedback written by users about a place.

Attributes include:

reviewer

place

rating

comment

Each review is associated with a specific place and user.

Amenity

Represents additional features available in a place.

Attributes include:

name

description

Amenities describe services or facilities available in a property.

API Interaction

The application processes requests through a sequence of interactions between the client, API controller, business logic components, repositories, and the database.

Examples of operations include:

User registration

Place creation

Review submission

Each operation follows a structured flow where the API validates requests, business logic processes the operation, and repositories manage database access.

Design Principles

This project follows several important software design principles.

Object-Oriented Programming

Encapsulation, abstraction, and modular design are used to organize system components.

Layered Architecture

Separates responsibilities across presentation, business logic, and persistence layers.

Facade Pattern

The API acts as a simplified interface for interacting with the system’s internal components.

Repository Pattern

Repositories manage database operations independently from business logic.

Documentation

The project includes technical documentation describing:

System architecture

Class diagrams

Sequence diagrams

API interaction flows

These diagrams illustrate the structure of the system and how components interact.

## Author
Eloy A. Alicea Sanchez
