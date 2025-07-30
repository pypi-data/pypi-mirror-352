# Help for bdcdata

## Getting started

To use the BDC data you need to have an api key. To get this key log into the Broadband Data Collection System (https://bdc.fcc.gov), click on your name in the top right corner and then select "Manage API Access". This will give you back an API key to enter into an environment variable.

After you have the key create a .env file in your projects base directory. There is an included example file (.env.sample).

```Dotenv
BDC_API_KEY='*API_HASH_KEY*'
BDC_USERNAME='*EMAIL*'
```