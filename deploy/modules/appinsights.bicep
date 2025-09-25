
param location string
param name string

resource comp 'Microsoft.Insights/components@2022-06-15' = {
  name: name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    IngestionMode: 'LogAnalytics'
  }
}

output instrumentationKey string = comp.properties.InstrumentationKey
