# Obtaining Credentials
In order to use this library you will need an API key or OAuth credentials. This guide walks through how to obtain 
these credentials.

## Prerequisites 
1. To access the Google API Console, you will need a [Google Account](https://www.google.com/accounts/NewAccount).
2. Go to [console.developers.google.com](https://console.developers.google.com) and [create a new project](https://console.cloud.google.com/projectcreate). 
Call it whatever you want, optionally set an organisation and click **Create**.
3. Find the "APIs" panel and click [**Go to APIs overview**](https://console.cloud.google.com/apis/enabled?project=turorial-walkthrough&show=all). 
4. Find and click the **ENABLE APIS AND SERVICES** button. Search for "youtube data api v3" and press enter. 
One result should be called **YouTube Data API v3**, click on it and then click the **ENABLE** button. 
You will be taken back to the "APIs and services" page.

## Obtaining An API Key
1. Navigate to the [**Credentials**](https://console.cloud.google.com/apis/credentials) page.
2. Find and click the 
**CREATE CREDENTIALS** button and select **API key**.

You have now created an API key. See the [examples](examples.md) for using an API Key.

## Obtaining OAuth Credentials

### OAuth Consent Screen

First, you will need to set up an OAuth consent screen:
1. Navigate to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2. Select **External** and click **CREATE**. 
3. Call the app name anything and select your email. You will also need to provide an email address under "Developer contact information".
4. Click **SAVE AND CONTINUE**.
5. For scopes, click **ADD OR REMOVE SCOPES**.
6. Find and search for "https://www.googleapis.com/auth/youtube".
7. Check the box for "YouTube Data API v3" and then click **UPDATE**.
8. Click **SAVE AND CONTINUE**.
9. For test users, click **ADD USERS** and add your gmail address.
10. Click **SAVE AND CONTINUE** and then **BACK TO DASHBOARD**

You have now set up an OAuth consent screen. You can now go ahead and create OAuth2 credentials.

### Creating Credentials
1. Navigate to the [**Credentials**](https://console.cloud.google.com/apis/credentials) page.
2. Find and click the 
**CREATE CREDENTIALS** button and select **OAuth client ID**.
3. Set "Desktop app" as the application type and click **CREATE**.

You have now created OAuth2 credentials. See the [examples](examples.md) for using an OAuth credentials.

