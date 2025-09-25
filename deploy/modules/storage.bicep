
param location string
param name string
param queueName string

resource sa 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
  }
}

resource c1 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${name}/default/images-entry'
  properties: { publicAccess: 'None' }
}
resource c2 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${name}/default/images-exit'
  properties: { publicAccess: 'None' }
}
resource c3 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-01-01' = {
  name: '${name}/default/${queueName}'
}

output connectionString string = 'DefaultEndpointsProtocol=https;AccountName=${name};EndpointSuffix=${environment().suffixes.storage};AccountKey='
