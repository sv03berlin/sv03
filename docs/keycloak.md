# Add attributes to profile scope

Add all required attributes to profile.
Client Scopes -> Profile -> Mappers -> Add Mapper -> By Configuration -> User-Attribute

Make sure management admin account for sync has `client consent` disabled.

## How to configure an environment
### Create a new Client

In this example this is done for a stage environment.

![](keycloak-screenshot/image.png)
![](keycloak-screenshot/image-1.png)
![](keycloak-screenshot/image-2.png)
Make sure the `Client authentication` is enabled and saved.
![](keycloak-screenshot/image-3.png)
Now a `Credentials` tab should show:
![](keycloak-screenshot/image-4.png)
Fill in the `Client Secret` and realm name into the `.env` or `docker-compose.yaml`.
Enable `client consent` to show the user what the app reads.
Login Theme Should be Keywind

Now the login environment is configured. Now we need to configure the back channel user update.

## Importer
### Create a Service Account for Importer

![](keycloak-screenshot/image-5.png)
Set a new Password.
![](keycloak-screenshot/image-6.png)
Assign a new Role:
![](keycloak-screenshot/image-7.png)
Assign `realm-management admin`
![](keycloak-screenshot/image-8.png)

### Create a new Client for Importer

![](keycloak-screenshot/image-9.png)
![](keycloak-screenshot/image-10.png)
![](keycloak-screenshot/image-11.png)
Make sure management admin account for sync has `client consent` disabled.
Enable `client authentication` and `authorization`

Assign `realm-management admin` within `service account roles` within the client for the importer.
![](keycloak-screenshot/image-12.png)
![](keycloak-screenshot/image-13.png)

Before using the importer make sure to configure the Email Settings for the realm.

## Add all User attributes set by importer to client scope

Go to Client Scope -> Profile
![](keycloak-screenshot/image-14.png)

Mappers -> Add Mapper -> By Configuration
![](keycloak-screenshot/image-15.png)

Create a new `User Attribute` mapper
![](keycloak-screenshot/image-16.png)

This needs to look like
![](keycloak-screenshot/image-17.png)

Repeat this for all attributes.
At time of writing these are:
- member_id
- mitgliedschaft
- managed_by
- birth_date
- clubboat
- boat

## Admin Permissions
Create a Admin group:
![](keycloak-screenshot/image-18.png)
Add Members:
![](keycloak-screenshot/image-19.png)

Create a Admin role:
![](keycloak-screenshot/image-20.png)

Assign Role to Group

![](keycloak-screenshot/image-21.png)

Add Members to group. After log out and log in the user should have the role in the client application.

## Membership Type, Groups and Admin matching
Membership Type is directly matched via name. Name from membership in Keycloak User == Name in Database.
For Group matching for reservations this is done via an internal name, which has to match the group name.
Members from the keycloak admin group will be superusers in clubapp.
For all groups managed, all attributes and membership types have a look at the importer.

## Invitation Link Duration
Per default an invitation link is 12h valid.
`Realm Settings -> Token -> Override Action Tokens`

## Configure Sync

The configuration of a service account for user sync is required to use keycloak client.
A `serviceaccount` needs to be created and a password is required.
This account needs the role `view-realm`.
