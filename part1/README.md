1. High-Level Architecture Diagram
This diagram illustrates the three-layer architecture of the HBnB application and the communication pathways between components mediated by the Facade pattern.

Code snippet
flowchart TB
    %% Presentation Layer
    subgraph PresentationLayer [Presentation Layer / API]
        direction LR
        API[API Services & Endpoints]
        U_API[User API]
        P_API[Place API]
        R_API[Review API]
        A_API[Amenity API]
        API --- U_API & P_API & R_API & A_API
    end

    %% Business Logic Layer
    subgraph BusinessLogicLayer [Business Logic Layer]
        Facade[HBnB Facade Interface]

        subgraph Models [Core Models]
            M_User[User Model]
            M_Place[Place Model]
            M_Review[Review Model]
            M_Amenity[Amenity Model]
        end
    end

    %% Persistence Layer
    subgraph PersistenceLayer [Persistence Layer]
        direction LR
        subgraph Repositories [Repositories / DAOs]
            R_User[User Repository]
            R_Place[Place Repository]
            R_Review[Review Repository]
            R_Amenity[Amenity Repository]
        end
        DB[(Database)]
        Repositories --> DB
    end

    %% Layer Interactions via Facade
    PresentationLayer ==>|1. Requests| Facade
    Facade ==>|2. Domain Logic| Models
    Facade ==>|3. Persistence| Repositories

    %% Visual Styling Colors
    style PresentationLayer fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style BusinessLogicLayer fill:#f0fdf4,stroke:#15803d,stroke-width:2px
    style PersistenceLayer fill:#fff7ed,stroke:#c2410c,stroke-width:2px
    style Facade fill:#fef08a,stroke:#a16207,stroke-width:2px,stroke-dasharray: 5 5
    style DB fill:#ffedd5,stroke:#ea580c,stroke-width:1px
    style API fill:#dbeafe,stroke:#2563eb,stroke-width:1px
2. Business Logic Class Diagram
This diagram details the core business entities (User, Place, Review, Amenity), their key attributes, operational methods, and domain relationships extending from a unified BaseModel.

Code snippet
classDiagram
    class BaseModel {
        +string id
        +datetime created_at
        +datetime updated_at
        +save() void
        +to_dict() dict
    }

    class User {
        +string first_name
        +string last_name
        +string email
        +string password
        +bool is_admin
        +register() bool
    }

    class Place {
        +string title
        +string description
        +float price
        +string address
        +int max_guests
        +string owner_id
    }

    class Review {
        +string comment
        +int rating
        +string place_id
        +string user_id
    }

    class Amenity {
        +string name
        +string description
    }

    %% Inheritance / Generalization
    BaseModel <|-- User : Inherits UUID and timestamps
    BaseModel <|-- Place : Inherits UUID and timestamps
    BaseModel <|-- Review : Inherits UUID and timestamps
    BaseModel <|-- Amenity : Inherits UUID and timestamps

    %% Entity Multiplicities
    User "1" --> "0..*" Place : owner / manages
    User "1" --> "0..*" Review : reviewer / author
    Place "1" *-- "0..*" Review : contains (Composition)
    Place "0..*" --> "0..*" Amenity : possesses / offers

    %% Diagram Styling Colors
    style BaseModel fill:#f1f5f9,stroke:#64748b,stroke-width:2px
    style User fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style Place fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style Review fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style Amenity fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
3. API Interaction Flow (Sequence Diagrams)
These diagrams trace the exact runtime step-by-step information workflow navigating across system boundaries via the HBnBFacade.

👤 User Registration Flow
Code snippet
sequenceDiagram
    autonumber
    actor Client as Client / User
    participant API as Presentation Layer<br>(User API)
    participant Facade as Facade<br>(HBnBFacade)
    participant Model as Business Layer<br>(User Model)
    participant DB as Persistence Layer<br>(UserRepository)

    Client->>API: POST /api/v1/users (user_data)
    activate API
    API->>API: Validate input format<br>(Valid email, secure password)

    API->>Facade: register_user(user_data)
    activate Facade

    Facade->>DB: get_by_email(email)
    activate DB
    DB-->>Facade: Returns User or Null
    deactivate DB

    alt Email already exists in the system
        Facade-->>API: Throw Exception (Email already registered)
        API-->>Client: HTTP 400 Bad Request (Error: Email in use)
    else Email available and valid
        Facade->>Model: Instantiate User(data)
        activate Model
        Model->>Model: Hash Password<br>Generate UUID4 & timestamps
        Model-->>Facade: User Object Created
        deactivate Model

        Facade->>DB: save(user_object)
        activate DB
        DB-->>Facade: Confirm save success
        deactivate DB

        Facade-->>API: Return created user data
        deactivate Facade
        API-->>Client: HTTP 201 Created (ID, Name, Email, etc.)
    end
    deactivate API
🏡 Place Creation Flow
Code snippet
sequenceDiagram
    autonumber
    actor Host as Host (User)
    participant API as Presentation Layer<br>(Place API)
    participant Facade as Facade<br>(HBnBFacade)
    participant DB_User as Persistence Layer<br>(UserRepository)
    participant Model as Business Layer<br>(Place Model)
    participant DB_Place as Persistence Layer<br>(PlaceRepository)

    Host->>API: POST /api/v1/places (place_data, owner_id)
    activate API

    API->>Facade: create_place(place_data, owner_id)
    activate Facade

    Facade->>DB_User: get_by_id(owner_id)
    activate DB_User
    DB_User-->>Facade: Returns User object (or Null)
    deactivate DB_User

    alt Owner ID does not exist
        Facade-->>API: Throw Exception (User not found)
        API-->>Host: HTTP 404 Not Found (Invalid property owner)
    else Valid User
        Facade->>Model: Instantiate Place(data, owner_id)
        activate Model
        Model->>Model: Validate coordinates & price<br>Generate UUID4
        Model-->>Facade: Place Object Created
        deactivate Model

        Facade->>DB_Place: save(place_object)
        activate DB_Place
        DB_Place-->>Facade: Confirm save success
        deactivate DB_Place

        Facade-->>API: Return created place data
        deactivate Facade
        API-->>Host: HTTP 201 Created (Place Details)
    end
    deactivate API
⭐ Review Submission Flow
Code snippet
sequenceDiagram
    autonumber
    actor Guest as Guest (User)
    participant API as Presentation Layer<br>(Review API)
    participant Facade as Facade<br>(HBnBFacade)
    participant DB as Persistence Layer<br>(User/Place Repos)
    participant Model as Business Layer<br>(Review Model)
    participant DB_Rev as Persistence Layer<br>(ReviewRepository)

    Guest->>API: POST /api/v1/places/{place_id}/reviews (comment, rating, user_id)
    activate API

    API->>Facade: add_review(place_id, user_id, comment, rating)
    activate Facade

    Facade->>DB: Verify User and Place existence
    activate DB
    DB-->>Facade: Both exist (Validation Successful)
    deactivate DB

    Facade->>Model: Instantiate Review(comment, rating, place_id, user_id)
    activate Model
    Model->>Model: Validate score range (1 to 5)
    Model-->>Facade: Review Object Ready
    deactivate Model

    Facade->>DB_Rev: save(review_object)
    activate DB_Rev
    DB_Rev-->>Facade: Confirm save success
    deactivate DB_Rev

    Facade-->>API: Return review confirmation
    deactivate Facade
    API-->>Guest: HTTP 201 Created (Review saved successfully)
    deactivate API
🔍 Fetching a List of Places Flow
Code snippet
sequenceDiagram
    autonumber
    actor Client as Client / User
    participant API as Presentation Layer<br>(Place API)
    participant Facade as Facade<br>(HBnBFacade)
    participant DB as Persistence Layer<br>(PlaceRepository)

    Client->>API: GET /api/v1/places?city=Paris (Optional filters)
    activate API

    API->>Facade: get_all_places(filters)
    activate Facade

    Facade->>DB: get_all() or get_filtered(filters)
    activate DB
    DB-->>Facade: Collection of Place objects (Raw Data)
    deactivate DB

    alt Data collection is empty
        Facade-->>API: Return empty list []
        API-->>Client: HTTP 200 OK []
    else Contains property records
        Facade->>Facade: Format/Serialize raw objects to clean dictionaries
        Facade-->>API: Return formatted place list
        deactivate Facade
        API-->>Client: HTTP 200 OK [ {place1}, {place2}, ... ]
    end
    deactivate API
