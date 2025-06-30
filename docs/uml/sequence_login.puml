@startuml
actor User
boundary "Flask App" as App
control "AuthController" as Auth

User -> App: Request login
App -> Auth: Validate credentials
Auth --> App: Return success or fail
App --> User: Redirect to dashboard
@enduml
