
param location string
param storageAccountName string
param queueName string = 'ingest'
param containerAppsEnvName string
param webAppName string

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    location: location
    name: storageAccountName
    queueName: queueName
  }
}

module appins 'modules/appinsights.bicep' = {
  name: 'appins'
  params: {
    location: location
    name: '${webAppName}-ai'
  }
}

module web 'modules/webapp.bicep' = {
  name: 'webapp'
  params: {
    location: location
    name: webAppName
    appInsightsKey: appins.outputs.instrumentationKey
  }
}

output storageConnection string = storage.outputs.connectionString
